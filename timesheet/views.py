from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.database import get_user_profile_mongo, get_group_members
from accounts.decorators import permission_required
from .database import (
    get_user_first_effective_date, save_timesheet, get_user_timesheets, 
    get_it_returns, get_certificates, get_client_names,
    get_other_forms, get_proceedings, get_tds, delete_timesheet_entry as db_delete_timesheet_entry,
)
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.contrib.auth import get_user_model
import json
from django.core.serializers.json import DjangoJSONEncoder


def is_group_head(user):
    return user.groups.filter(name='Group Head').exists()

def is_super_group_head(user):
    return user.groups.filter(name='Super Group Head').exists()

def is_admin(user):
    return user.groups.filter(name='Super Admin').exists()

# Create your views here.
@permission_required('timesheet', 'view')
def fill_timesheet(request):
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    user_effective_date = get_user_first_effective_date(request.user.id)
    
    if request.method == 'POST':
        hours = float(request.POST.get('hours', 0))
        
        # Get values from the first form
        entry_date = datetime.strptime(request.POST.get('date'), '%Y-%m-%d')
        entry_date = entry_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate total hours first
        time_in = request.POST.get('time_in')
        time_out = request.POST.get('time_out')
        time_in_obj = datetime.strptime(time_in, '%H:%M')
        time_out_obj = datetime.strptime(time_out, '%H:%M')
        total_hours = (time_out_obj - time_in_obj).seconds / 3600
        
        # Only check pending days if trying to submit for today
        if entry_date >= today:
            days_with_pending = 0
            days_checked = 0
            check_date = today
            while days_checked < 7:
                if check_date.weekday() != 6:  # Not Sunday
                    daily_entries = get_user_timesheets(request.user.id, check_date)
                    if daily_entries:
                        # Check if the last entry of the day has pending_hours set to 0
                        last_entry = daily_entries[0]  # get_user_timesheets returns sorted by created_at desc
                        if last_entry.get('pending_hours', 0) - last_entry.get('hours', 0) > 0:  # If pending_hours is not 0
                            days_with_pending += 1
                    else:
                        # If no entries exist for the day, consider it as pending
                        days_with_pending += 1
                    days_checked += 1
                check_date -= timedelta(days=1)
            
            if days_with_pending >= 7:
                messages.error(request, 'Cannot submit timesheet for today. You have pending hours for more than 7 days. Please complete previous timesheets first.')
                return redirect('fill_timesheet')
        
        # Calculate utilized and pending hours
        existing_entries = get_user_timesheets(request.user.id, entry_date)
        utilized_hours = sum(entry.get('hours', 0) for entry in existing_entries)
        pending_hours = total_hours - utilized_hours

        reason = request.POST.get('reason', '').upper()
        
        # Check if pending hours are negative
        if pending_hours < 0:
            messages.error(request, 'Cannot submit timesheet when pending hours are negative')
            return redirect('fill_timesheet')
            
        # Check if new hours exceed pending hours
        if hours > pending_hours:
            messages.error(request, f'Hours cannot exceed pending hours ({pending_hours})')
            return redirect('fill_timesheet')
        
        timesheet_data = {
            'user_id': str(request.user.id),
            'date': entry_date,
            'reason': request.POST.get('reason', '').upper(),
            'time_in': request.POST.get('time_in'),
            'time_out': request.POST.get('time_out'),
            'client_name': request.POST.get('client_name'),
            'task': request.POST.get('task'),
            'assignment': request.POST.get('assignment_display'),
            'assignment_id': request.POST.get('assignment'),
            'remarks': request.POST.get('remarks', '').upper(),
            'hours': hours,
            'pending_hours': pending_hours,
            'reason': reason,
        }
        
        save_timesheet(timesheet_data)
        messages.success(request, 'Timesheet entry saved successfully!')
        return redirect('fill_timesheet')
    
    context = {
        'user_effective_date':user_effective_date,
        'today': today,
        'client_names': get_client_names(),
    }
    return render(request, 'fill_timesheet.html', context)


@permission_required('timesheet', 'view')
def get_assignments(request):
    client_name = request.GET.get('client_name')
    task_type = request.GET.get('task_type')
    
    if not client_name or not task_type:
        return JsonResponse({'error': 'Client name and task type are required'}, status=400)
    
    try:
        assignments = []
        if task_type == 'ROI':
            assignments = get_it_returns(client_name)
        elif task_type == 'Certificates':
            assignments = get_certificates(client_name)
        elif task_type == 'Other':
            assignments = get_other_forms(client_name)
        elif task_type == 'TDS':
            assignments = get_tds(client_name)
        elif task_type == 'Proceedings':
            assignments = get_proceedings(client_name)
        return JsonResponse({'assignments': assignments})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

#Give date and user id, return time in and time out for that day's first entry, if it doesn't exist, return default time in and time out

@permission_required('timesheet', 'view')
def get_time_settings(request):
    
    date = datetime.strptime(request.GET.get('date'), '%Y-%m-%d')
    existing_entries = get_user_timesheets(request.user.id, date, limit=1)
    user_profile = get_user_profile_mongo(request.user.id)
    if existing_entries:
        time_in = existing_entries[0].get('time_in', user_profile.get('time_in', '09:00'))
        time_out = existing_entries[0].get('time_out', user_profile.get('time_out', '18:00'))
    else:
        time_in = user_profile.get('time_in', '09:00')
        time_out = user_profile.get('time_out', '18:00')
    return JsonResponse({'time_in': time_in, 'time_out': time_out})



@permission_required('timesheet', 'view')
def get_pending_entries(request):
    
    user_profile = get_user_profile_mongo(request.user.id)
    # Default time in and and time out and start date of employee
    default_time_in = user_profile.get('time_in', '09:00')
    default_time_out = user_profile.get('time_out', '18:00')
    user_start_date = user_profile.get('effective_date')
    

    # Get entries for the last 7 days or until start date
    pending_entries = []
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Calculate the start date for checking (either user's start date or 7 days ago)
    start_check_date = user_start_date if user_start_date else today - timedelta(days=7)
    
    # Get all timesheet entries for the date range in one query to reduce database calls
    from .database import db
    all_entries = list(db.timesheetMaster.find({
        'user_id': str(request.user.id),
        'date': {'$gte': start_check_date, '$lte': today}
    }).sort('date', -1).sort('created_at', -1))
    
    # Group entries by date for easier processing
    entries_by_date = {}
    for entry in all_entries:
        date_str = entry['date'].strftime('%Y-%m-%d')
        if date_str not in entries_by_date:
            entries_by_date[date_str] = []
        entries_by_date[date_str].append(entry)
    
    days_back = 0
    # Keep going back until we find 7 days with pending hours or hit user's start date
    while len(pending_entries) < 7:
        check_date = today - timedelta(days=days_back)
        if user_start_date and check_date < user_start_date:
            break
        if check_date.weekday() != 6:  # Skip Sundays
            date_str = check_date.strftime('%Y-%m-%d')
            daily_entries = entries_by_date.get(date_str, [])
            
            # Get time in/out from first entry of the day, or use defaults if no entries
            if daily_entries:
                first_entry = daily_entries[0]  # Get the first entry of the day
                time_in = first_entry.get('time_in', default_time_in)
                time_out = first_entry.get('time_out', default_time_out)
            else:
                time_in = default_time_in
                time_out = default_time_out
            
            # Calculate total hours for this specific day
            time_in_obj = datetime.strptime(time_in, '%H:%M')
            time_out_obj = datetime.strptime(time_out, '%H:%M')
            day_total_hours = (time_out_obj - time_in_obj).seconds / 3600
            
            daily_total = sum(entry.get('hours', 0) for entry in daily_entries)
            pending_hours = day_total_hours - daily_total
            
            # Only add days that have pending hours
            if pending_hours > 0:
               
                pending_entries.append({
                    'date': check_date.strftime('%d-%m-%Y'),
                    'day': check_date.strftime('%A'),
                    'pending_hours': pending_hours,
                })
        days_back += 1

    return JsonResponse({"data": pending_entries}, encoder=DjangoJSONEncoder)

@permission_required('timesheet', 'view')
def calculate_hours(request):
    error = False
    error_message = ''

    date = datetime.strptime(request.POST.get('date'), '%Y-%m-%d')
    # Get existing entries for the selected date
    existing_entries = get_user_timesheets(request.user.id, date, id=True)
    
    # Use 9am and 6pm if request does not have time in time out
    time_in = request.POST.get('time_in', '09:00')
    time_out = request.POST.get('time_out', '18:00')

    # Calculate total hours
    time_in_obj = datetime.strptime(time_in, '%H:%M')
    time_out_obj = datetime.strptime(time_out, '%H:%M')
    total_hours = (time_out_obj - time_in_obj).seconds / 3600

    utilized_hours = sum(entry.get('hours', 0) for entry in existing_entries)
    pending_hours = total_hours - utilized_hours

    if utilized_hours > total_hours:
        error = True
        error_message = "Your total hours can not be less than utilzed hours"


    response_data = {
        'total_hours': total_hours,
        'utilized_hours': utilized_hours,
        'pending_hours': pending_hours,
        'time_in': time_in,
        'time_out': time_out,
        'success': True,
        'date_entries': existing_entries,
        'error': error,
        'error_message': error_message
    }

    return JsonResponse(response_data, encoder=DjangoJSONEncoder)


@permission_required('timesheet', 'view')
def employee_corner(request):
    User = get_user_model()
    
    # Get selected date from request, default to today
    selected_date = request.GET.get('date')
    if selected_date:
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d')
    else:
        selected_date = datetime.now()
    selected_date = selected_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Get all active users based on role
    if is_super_group_head(request.user) or request.user.is_superuser:
        # Super group head can see all users except admins
        all_users = User.objects.filter(is_active=True).exclude(
            groups__name__in=['Super Admin', 'Admin']
        )
    elif is_group_head(request.user):
        # Get members of the group head's groups
        member_ids = get_group_members(str(request.user.id))
        all_users = User.objects.filter(
            id__in=member_ids,
            is_active=True
        )
    else:
        # If not a group head or super group head, return empty
        all_users = User.objects.none()
    
    user_data = []
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Pre-fetch all user profiles to reduce database calls
    user_profiles = {}
    for user in all_users:
        user_profiles[user.id] = get_user_profile_mongo(user.id)
    
    # Get all timesheet entries for all users for the selected date and recent dates for pending calculation
    from .database import db
    user_ids = [str(user.id) for user in all_users]
    
    # Calculate the start date for pending days calculation (7 days ago or user's start date)
    min_start_date = today - timedelta(days=7)
    for user in all_users:
        user_profile = user_profiles[user.id]
        user_start_date = user_profile.get('effective_date')
        if user_start_date and user_start_date < min_start_date:
            min_start_date = user_start_date
    
    # Fetch all timesheet entries for the date range
    all_timesheet_entries = list(db.timesheetMaster.find({
        'user_id': {'$in': user_ids},
        'date': {'$gte': min_start_date, '$lte': today}
    }, {'_id': 0}).sort('date', -1).sort('created_at', -1))
    
    # Group entries by user and date for easier processing
    entries_by_user_date = {}
    for entry in all_timesheet_entries:
        user_id = entry['user_id']
        date_str = entry['date'].strftime('%Y-%m-%d')
        if user_id not in entries_by_user_date:
            entries_by_user_date[user_id] = {}
        if date_str not in entries_by_user_date[user_id]:
            entries_by_user_date[user_id][date_str] = []
        entries_by_user_date[user_id][date_str].append(entry)
    
    for user in all_users:
        user_profile = user_profiles[user.id]
        default_time_in = user_profile.get('time_in', '09:00')
        default_time_out = user_profile.get('time_out', '18:00')
        user_start_date = user_profile.get('effective_date')
        
        # Get timesheet entries for selected date
        selected_date_str = selected_date.strftime('%Y-%m-%d')
        daily_entries = entries_by_user_date.get(str(user.id), {}).get(selected_date_str, [])
        
        # Get time in/out from first entry of the selected date, or use defaults if no entries
        if daily_entries:
            first_entry = daily_entries[0]  # Get the first entry of the day
            time_in = first_entry.get('time_in', default_time_in)
            time_out = first_entry.get('time_out', default_time_out)
        else:
            time_in = default_time_in
            time_out = default_time_out
        
        # Calculate standard hours for the selected date
        time_in_obj = datetime.strptime(time_in, '%H:%M')
        time_out_obj = datetime.strptime(time_out, '%H:%M')
        standard_hours = (time_out_obj - time_in_obj).seconds / 3600
        
        daily_total = sum(entry.get('hours', 0) for entry in daily_entries)
        pending_hours = standard_hours - daily_total if selected_date.weekday() != 6 else 0
        
        # Calculate pending days from user's start date or last 7 days, whichever is more recent
        start_check_date = user_start_date if user_start_date else today - timedelta(days=7)
        days_with_pending = 0
        total_pending_days = 0
        check_date = today
        
        user_entries = entries_by_user_date.get(str(user.id), {})
        
        while check_date >= start_check_date:
            if check_date.weekday() != 6:  # Skip Sunday
                check_date_str = check_date.strftime('%Y-%m-%d')
                day_entries = user_entries.get(check_date_str, [])
                
                # Get time in/out from first entry of this day, or use defaults if no entries
                if day_entries:
                    first_day_entry = day_entries[0]
                    day_time_in = first_day_entry.get('time_in', default_time_in)
                    day_time_out = first_day_entry.get('time_out', default_time_out)
                else:
                    day_time_in = default_time_in
                    day_time_out = default_time_out
                
                # Calculate standard hours for this specific day
                day_time_in_obj = datetime.strptime(day_time_in, '%H:%M')
                day_time_out_obj = datetime.strptime(day_time_out, '%H:%M')
                day_standard_hours = (day_time_out_obj - day_time_in_obj).seconds / 3600
                
                day_total = sum(entry.get('hours', 0) for entry in day_entries)
                if day_standard_hours - day_total > 0:
                    days_with_pending += 1
                total_pending_days += 1
            check_date -= timedelta(days=1)
        
        # Serialize timesheet entries for JavaScript
        serialized_entries = json.dumps(daily_entries, cls=DjangoJSONEncoder)
        
        user_data.append({
            'user': user,
            'timesheet_entries': daily_entries,
            'serialized_entries': serialized_entries,
            'total_hours': daily_total,
            'pending_hours': round(pending_hours, 2),
            'standard_hours': standard_hours,
            'is_critical': days_with_pending >= 7,
            'days_with_pending': days_with_pending,
            'total_pending_days': total_pending_days,
            'start_date': start_check_date.strftime('%Y-%m-%d') if start_check_date else None
        })
    
    # Sort users by pending hours and critical status
    user_data.sort(key=lambda x: (-x['is_critical'], -x['pending_hours']))
    
    context = {
        'user_data': user_data,
        'selected_date': selected_date,
        'is_super_group_head': is_super_group_head(request.user),
        'today': datetime.now()
    }
    
    return render(request, 'employee_corner.html', context)

@permission_required('timesheet', 'view')
def delete_timesheet_entry(request):
    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        success = db_delete_timesheet_entry(entry_id, str(request.user.id))
        if success:
            return JsonResponse({'status': 'success', 'message': 'Record deleted successfully.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Record not found.'}, status=404)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)