import json
import math
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse, HttpRequest
from django.shortcuts import render, redirect
from django.db.models import Q

from accounts.database import get_user_profile_mongo, get_group_members, get_groups_for_head, get_users_by_role, get_all_groups, is_timesheet_mandatory, set_timesheet_mandatory, get_non_mandatory_dates
from accounts.roles import ROLE_HIERARCHY
from accounts.decorators import permission_required
from .database import (
    get_user_first_effective_date,
    save_timesheet,
    get_user_timesheets,
    get_it_returns,
    get_certificates,
    get_client_names,
    get_other_forms,
    get_proceedings,
    get_tds,
    delete_timesheet_entry as db_delete_timesheet_entry,
    mark_optional_days,
    mark_period_optional,
    unmark_optional_days,
    get_optional_dates,
    get_optional_days_detail,
    has_allocations,
    get_last_allocation_map,
    create_allocations,
    get_my_allocations,
    count_pending_verifications,
    get_allocation,
    decide_allocation,
    get_verification_log,
    get_verification_employees,
    get_week_entries,
)


def is_group_head(user) -> bool:
    """Check if user is a Group Head."""
    return user.groups.filter(name='Group Head').exists()


def is_super_group_head(user) -> bool:
    """Check if user is a Super Group Head."""
    return user.groups.filter(name='Super Group Head').exists()


def is_admin(user) -> bool:
    """Check if user is a Super Admin."""
    return user.groups.filter(name='Super Admin').exists()


def _can_mark_optional(request) -> bool:
    """Only Super Group Head / Super Admin (or superuser) may mark optional days."""
    return is_super_group_head(request.user) or is_admin(request.user) or request.user.is_superuser


def _actor_rank(request) -> int:
    """Rank of the requesting user (lower = higher authority); 0 for admin/superuser."""
    if is_admin(request.user) or request.user.is_superuser:
        return 0
    profile = get_user_profile_mongo(request.user.id)
    role = profile.get('role', '') if profile else ''
    return ROLE_HIERARCHY.get(role, 99)


def _target_rank(target_user_id):
    """Rank of a target user from their Mongo profile, or None if the profile is missing."""
    profile = get_user_profile_mongo(target_user_id)
    if not profile:
        return None
    return ROLE_HIERARCHY.get(profile.get('role', ''), 99)


def _is_verifier(user) -> bool:
    """Group Heads and Super Group Heads receive weekly verification allocations."""
    return is_group_head(user) or is_super_group_head(user)


def _can_see_all_logs(user) -> bool:
    """Super Group Head / Super Admin / superuser oversee every verification."""
    return is_super_group_head(user) or is_admin(user) or user.is_superuser


def _previous_week_start():
    """Monday (midnight) of the most recently completed Mon-Sat week."""
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    return today - timedelta(days=today.weekday()) - timedelta(days=7)


def _ensure_weekly_allocation(user):
    """Lazily create this verifier's random sample for the previous completed week.

    Runs on every My Verifications load; the has_allocations check plus the unique
    index behind create_allocations make it idempotent. Only the immediately
    previous week is generated - older pending allocations never expire, so a week
    the verifier never opened is skipped deliberately, not lost.
    """
    week_start = _previous_week_start()
    if week_start < settings.TIMESHEET_START_DATE:
        return
    if has_allocations(user.id, week_start):
        return

    if is_super_group_head(user):
        pool_ids = get_users_by_role('Group Head')
        verifier_role = 'Super Group Head'
    elif is_group_head(user):
        pool_ids = get_group_members(str(user.id))
        verifier_role = 'Group Head'
    else:
        return
    if not pool_ids:
        return

    week_end = week_start + timedelta(days=5)
    User = get_user_model()
    candidates = []
    for member in User.objects.filter(id__in=pool_ids, is_active=True).exclude(id=user.id):
        profile = get_user_profile_mongo(member.id)
        if not profile:
            continue
        if not is_timesheet_mandatory(profile):
            continue  # not required to fill timesheets -> nothing to verify
        effective_date = profile.get('effective_date')
        if effective_date and effective_date > week_end:
            continue  # joined after the week being verified
        candidates.append((member, profile))
    if not candidates:
        return

    k = min(len(candidates), max(1, math.ceil(0.25 * len(candidates))))
    last_allocated = get_last_allocation_map(user.id, [str(m.id) for m, _ in candidates])
    random.shuffle(candidates)
    # Stable sort after the shuffle: least-recently-reviewed first, random tie-break.
    candidates.sort(key=lambda c: last_allocated.get(str(c[0].id), datetime.min))

    create_allocations([
        {
            'week_start': week_start,
            'week_end': week_end,
            'employee_id': str(member.id),
            'employee_name': member.get_full_name() or member.username,
            'employee_role': profile.get('role', ''),
            'verifier_id': str(user.id),
            'verifier_name': user.get_full_name() or user.username,
            'verifier_role': verifier_role,
            'groups': profile.get('groups', []),
            'allocation_method': 'random_lru',
        }
        for member, profile in candidates[:k]
    ])


def _expand_optional_dates(mode, request):
    """Build the list of working-day midnight datetimes (Sundays skipped) for a mode.

    mode 'day' -> POST['date']; 'range' -> POST['start_date']..POST['end_date'] inclusive;
    'week' -> Mon..Sat of the week containing POST['week_start'] (or POST['date']).
    Returns (dates, error_message).
    """
    def _parse(name):
        raw = request.POST.get(name)
        if not raw:
            return None
        return datetime.strptime(raw, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)

    dates = []
    if mode == 'day':
        d = _parse('date')
        if not d:
            return None, 'A date is required.'
        if d.weekday() != 6:  # skip Sunday
            dates.append(d)
    elif mode == 'range':
        start = _parse('start_date')
        end = _parse('end_date')
        if not start or not end:
            return None, 'Start and end dates are required.'
        if end < start:
            return None, 'End date cannot be before start date.'
        cur = start
        while cur <= end:
            if cur.weekday() != 6:  # skip Sundays
                dates.append(cur)
            cur += timedelta(days=1)
    elif mode == 'week':
        anchor = _parse('week_start') or _parse('date')
        if not anchor:
            return None, 'A date within the week is required.'
        monday = anchor - timedelta(days=anchor.weekday())
        dates = [monday + timedelta(days=i) for i in range(6)]  # Mon..Sat
    else:
        return None, 'Invalid selection mode.'
    return dates, None

# Create your views here.


@permission_required('timesheet', 'view')
def fill_timesheet(request: HttpRequest):
    """Handle timesheet entry form submission and display."""
    today = datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0
    )
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
        

        # Calculate utilized and pending hours
        existing_entries = get_user_timesheets(request.user.id, entry_date)
        utilized_hours = sum(entry.get('hours', 0) for entry in existing_entries)
        pending_hours = total_hours - utilized_hours

        reason = request.POST.get('reason', '').upper()
        
        # Check for pending timesheets from previous 7 days
        user_profile = get_user_profile_mongo(request.user.id)
        if not user_profile:
            messages.error(request, 'User profile not found. Please contact administrator.')
            return redirect('fill_timesheet')

        if is_timesheet_mandatory(user_profile):
            user_start_date = user_profile.get('effective_date')
            window_start = user_start_date if user_start_date else today - timedelta(days=14)
            optional_set = get_optional_dates(request.user.id, window_start, today)
            # Days in a past non-mandatory period stay excused even after the user is mandatory again.
            optional_set |= get_non_mandatory_dates(user_profile, window_start, today)
            days_checked = 0
            days_with_pending = 0
            check_date = today - timedelta(days=1)
            
            # Only check previous days if we're entering for today
            if entry_date == today:
                while days_checked < 7:
                    # Stop checking if we hit the user's start date
                    if user_start_date and check_date < user_start_date:
                        break
                        
                    if check_date.weekday() != 6 and check_date not in optional_set:  # Not Sunday, not optional
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
                    
                if days_with_pending > 0:
                    messages.error(
                        request,
                        f'You cannot fill out a timesheet. You have pending hours for {days_with_pending} of the last 7 days.'
                    )
                    return redirect('fill_timesheet')

        # Check if pending hours are negative
        if pending_hours < 0:
            messages.error(request, 'Cannot submit timesheet when pending hours are negative')
            return redirect('fill_timesheet')
            
        # Check if new hours exceed pending hours
        if hours > pending_hours:
            messages.error(
                request,
                f'Hours cannot exceed pending hours ({pending_hours})'
            )
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
        'user_effective_date': user_effective_date,
        'today': today,
        'client_names': get_client_names(),
        'pending_verification_count': count_pending_verifications(request.user.id) if _is_verifier(request.user) else 0,
    }
    return render(request, 'fill_timesheet.html', context)


@permission_required('timesheet', 'view')
def get_assignments(request: HttpRequest) -> JsonResponse:
    """Get assignments based on client name and task type."""
    client_name = request.GET.get('client_name')
    task_type = request.GET.get('task_type')
    
    if not client_name or not task_type:
        return JsonResponse(
            {'error': 'Client name and task type are required'},
            status=400
        )
    
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

# Give date and user id, return time in and time out for that day's first entry,
# if it doesn't exist, return default time in and time out


@permission_required('timesheet', 'view')
def get_time_settings(request: HttpRequest) -> JsonResponse:
    """Get time settings for a specific date."""
    date = datetime.strptime(request.GET.get('date'), '%Y-%m-%d')
    existing_entries = get_user_timesheets(
        request.user.id, date, limit=1
    )
    user_profile = get_user_profile_mongo(request.user.id)
    
    if existing_entries:
        time_in = existing_entries[0].get(
            'time_in', user_profile.get('time_in', '09:00')
        )
        time_out = existing_entries[0].get(
            'time_out', user_profile.get('time_out', '18:00')
        )
    else:
        time_in = user_profile.get('time_in', '09:00')
        time_out = user_profile.get('time_out', '18:00')
    
    return JsonResponse({'time_in': time_in, 'time_out': time_out})



@permission_required('timesheet', 'view')
def get_pending_entries(request: HttpRequest) -> JsonResponse:
    """Get pending timesheet entries for the user."""
    user_profile = get_user_profile_mongo(request.user.id)
    # Default time in and and time out and start date of employee
    default_time_in = user_profile.get('time_in', '09:00')
    default_time_out = user_profile.get('time_out', '18:00')
    user_start_date = user_profile.get('effective_date')

    # Get entries for the last 7 days or until start date
    pending_entries = []
    today = datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    
    # Calculate the start date for checking (either user's start date or 7 days ago)
    start_check_date = (
        user_start_date if user_start_date else today - timedelta(days=7)
    )
    optional_set = get_optional_dates(request.user.id, start_check_date, today)
    optional_set |= get_non_mandatory_dates(user_profile, start_check_date, today)

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
        if check_date.weekday() != 6 and check_date not in optional_set:  # Skip Sundays + optional
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

    return JsonResponse(
        {"data": pending_entries}, encoder=DjangoJSONEncoder
    )

@permission_required('timesheet', 'view')
def calculate_hours(request: HttpRequest) -> JsonResponse:
    """Calculate hours for timesheet entry."""
    error = False
    error_message = ''

    date = datetime.strptime(request.POST.get('date'), '%Y-%m-%d')
    # Get existing entries for the selected date
    existing_entries = get_user_timesheets(
        request.user.id, date, id=True
    )
    
    # Use 9am and 6pm if request does not have time in time out
    time_in = request.POST.get('time_in', '09:00')
    time_out = request.POST.get('time_out', '18:00')

    # Calculate total hours
    time_in_obj = datetime.strptime(time_in, '%H:%M')
    time_out_obj = datetime.strptime(time_out, '%H:%M')
    total_hours = (time_out_obj - time_in_obj).seconds / 3600

    utilized_hours = sum(
        entry.get('hours', 0) for entry in existing_entries
    )
    pending_hours = total_hours - utilized_hours

    if utilized_hours > total_hours:
        error = True
        error_message = (
            "Your total hours can not be less than utilzed hours"
        )


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
def employee_corner(request: HttpRequest):
    """Display employee corner with timesheet data for managers."""
    User = get_user_model()
    
    # Get selected date from request, default to today
    selected_date = request.GET.get('date')
    if selected_date:
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d')
    else:
        selected_date = datetime.now()
    selected_date = selected_date.replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    
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
    today = datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    
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

    # Prefetch optional days for all visible users in one query, grouped per user.
    optional_docs = db.optionalDayMaster.find({
        'user_id': {'$in': user_ids},
        'date': {'$gte': min_start_date, '$lte': today}
    }, {'_id': 0, 'user_id': 1, 'date': 1})
    optional_by_user = {}
    for doc in optional_docs:
        optional_by_user.setdefault(doc['user_id'], set()).add(doc['date'])

    # Fold each user's non-mandatory periods into their optional set so they are not
    # counted as pending/critical while (or after) being excused from timesheets.
    for user in all_users:
        non_mandatory = get_non_mandatory_dates(user_profiles[user.id], min_start_date, today)
        if non_mandatory:
            optional_by_user.setdefault(str(user.id), set()).update(non_mandatory)

    can_mark = _can_mark_optional(request)
    actor_rank = _actor_rank(request)

    for user in all_users:
        user_profile = user_profiles[user.id]
        default_time_in = user_profile.get('time_in', '09:00')
        default_time_out = user_profile.get('time_out', '18:00')
        user_start_date = user_profile.get('effective_date')
        user_optional = optional_by_user.get(str(user.id), set())
        
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
        pending_hours = standard_hours - daily_total if (selected_date.weekday() != 6 and selected_date not in user_optional) else 0
        
        # Calculate pending days from user's start date or last 7 days, whichever is more recent
        start_check_date = user_start_date if user_start_date else today - timedelta(days=7)
        days_with_pending = 0
        total_pending_days = 0
        check_date = today
        
        user_entries = entries_by_user_date.get(str(user.id), {})
        
        while check_date >= start_check_date:
            if check_date.weekday() != 6 and check_date not in user_optional:  # Skip Sunday + optional
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

        target_rank_val = ROLE_HIERARCHY.get(user_profile.get('role', ''), 99) if user_profile else 99
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
            'start_date': start_check_date.strftime('%Y-%m-%d') if start_check_date else None,
            'can_mark_optional': can_mark and actor_rank < target_rank_val,
            'optional_days': sorted(d.strftime('%Y-%m-%d') for d in user_optional),
        })
    
    # Sort users by pending hours and critical status
    user_data.sort(key=lambda x: (-x['is_critical'], -x['pending_hours']))
    
    context = {
        'user_data': user_data,
        'selected_date': selected_date,
        'is_super_group_head': is_super_group_head(request.user),
        'can_mark_optional': can_mark,
        'today': datetime.now(),
        'show_manager_tabs': _is_verifier(request.user) or _can_see_all_logs(request.user),
        'pending_verification_count': count_pending_verifications(request.user.id) if _is_verifier(request.user) else 0,
        'active_tab': 'overview',
    }

    return render(request, 'employee_corner.html', context)

@permission_required('timesheet', 'view')
def delete_timesheet_entry(request: HttpRequest) -> JsonResponse:
    """Delete a timesheet entry."""
    if request.method == 'POST':
        entry_id = request.POST.get('entry_id')
        success = db_delete_timesheet_entry(
            entry_id, str(request.user.id)
        )
        if success:
            return JsonResponse(
                {
                    'status': 'success',
                    'message': 'Record deleted successfully.'
                }
            )
        else:
            return JsonResponse(
                {
                    'status': 'error',
                    'message': 'Record not found.'
                },
                status=404
            )
    return JsonResponse(
        {
            'status': 'error',
            'message': 'Invalid request method.'
        },
        status=405
    )

@permission_required('timesheet', 'view')
def manage_mandatory_timesheets(request: HttpRequest):
    """View to allow higher roles to mark lower roles as timesheet_mandatory True/False"""
    if request.method == 'POST':
        target_user_id = request.POST.get('user_id')
        status = request.POST.get('status') == 'true'
        
        # Verify permissions
        current_profile = get_user_profile_mongo(request.user.id)
        current_role = current_profile.get('role', '') if current_profile else ''
        current_rank = ROLE_HIERARCHY.get(current_role, 99)
        
        if is_admin(request.user):
            current_rank = 0
            
        target_profile = get_user_profile_mongo(target_user_id)
        if not target_profile:
            return JsonResponse({'status': 'error', 'message': 'User profile not found'}, status=404)
        
        target_role = target_profile.get('role', '')
        target_rank = ROLE_HIERARCHY.get(target_role, 99)
        
        if current_rank >= target_rank:
            return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)

        changed = set_timesheet_mandatory(
            target_user_id, status, request.user.id, request.user.get_full_name()
        )
        # Switching off marks the user's whole timesheet history optional (see edit_user).
        if changed and not status:
            start = target_profile.get('effective_date') or settings.TIMESHEET_START_DATE
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            mark_period_optional(
                target_user_id, start, today,
                reason='TIMESHEET NOT MANDATORY',
                marked_by=request.user.id, marked_by_name=request.user.get_full_name(),
            )
        return JsonResponse({'status': 'success', 'message': 'Mandatory timesheet setting updated successfully.'})

    # GET request
    current_profile = get_user_profile_mongo(request.user.id)
    current_role = current_profile.get('role', '') if current_profile else ''
    current_rank = ROLE_HIERARCHY.get(current_role, 99)
    
    if is_admin(request.user):
        current_rank = 0  # Can see everyone
        
    User = get_user_model()
    # Exclude admins/superusers and current user
    all_active_users = User.objects.filter(is_active=True).exclude(
        groups__name__in=['Super Admin', 'Admin']
    ).exclude(id=request.user.id)
    
    manageable_users = []
    for u in all_active_users:
        profile = get_user_profile_mongo(u.id)
        if not profile:
            continue
        role = profile.get('role', '')
        rank = ROLE_HIERARCHY.get(role, 99)
        if rank > current_rank:
            manageable_users.append({
                'id': u.id,
                'name': f"{u.first_name} {u.last_name}",
                'username': u.username,
                'role': role,
                'timesheet_mandatory': is_timesheet_mandatory(profile)
            })
            
    return render(request, 'manage_mandatory_timesheets.html', {'users': manageable_users, 'current_role': current_role})


@permission_required('timesheet', 'view')
def mark_optional(request: HttpRequest) -> JsonResponse:
    """Mark an employee's day(s) as optional so they no longer count as pending."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)
    if not _can_mark_optional(request):
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)

    target_user_id = request.POST.get('user_id')
    target_rank = _target_rank(target_user_id)
    if target_rank is None:
        return JsonResponse({'status': 'error', 'message': 'User profile not found'}, status=404)
    if _actor_rank(request) >= target_rank:  # strictly lower-rank targets only (no self/peers)
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)

    dates, error = _expand_optional_dates(request.POST.get('mode', 'day'), request)
    if error:
        return JsonResponse({'status': 'error', 'message': error}, status=400)
    if not dates:
        return JsonResponse({'status': 'error', 'message': 'No working days selected.'}, status=400)

    count = mark_optional_days(
        target_user_id, dates,
        reason=request.POST.get('reason', ''),
        marked_by=request.user.id,
        marked_by_name=request.user.get_full_name(),
    )
    messages.success(request, f'Marked {count} day(s) as optional.')
    return JsonResponse({'status': 'success', 'marked': count})


@permission_required('timesheet', 'view')
def unmark_optional(request: HttpRequest) -> JsonResponse:
    """Remove optional-day mark(s) for an employee (single date or inclusive range)."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)
    if not _can_mark_optional(request):
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)

    target_user_id = request.POST.get('user_id')
    target_rank = _target_rank(target_user_id)
    if target_rank is None:
        return JsonResponse({'status': 'error', 'message': 'User profile not found'}, status=404)
    if _actor_rank(request) >= target_rank:
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)

    single = request.POST.get('date')
    if single:
        dates = [datetime.strptime(single, '%Y-%m-%d')]
    else:
        start = request.POST.get('start_date')
        end = request.POST.get('end_date')
        if not start or not end:
            return JsonResponse({'status': 'error', 'message': 'A date or date range is required.'}, status=400)
        start_d = datetime.strptime(start, '%Y-%m-%d')
        end_d = datetime.strptime(end, '%Y-%m-%d')
        dates = []
        cur = start_d
        while cur <= end_d:
            dates.append(cur)
            cur += timedelta(days=1)

    removed = unmark_optional_days(target_user_id, dates)
    messages.success(request, f'Removed optional mark from {removed} day(s).')
    return JsonResponse({'status': 'success', 'removed': removed})


@permission_required('timesheet', 'view')
def list_optional_days(request: HttpRequest) -> JsonResponse:
    """List an employee's optional days for the Employee Corner unmark panel."""
    if not _can_mark_optional(request):
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)

    target_user_id = request.GET.get('user_id')
    target_rank = _target_rank(target_user_id)
    if target_rank is None:
        return JsonResponse({'status': 'error', 'message': 'User profile not found'}, status=404)
    if _actor_rank(request) >= target_rank:
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    details = get_optional_days_detail(target_user_id, today - timedelta(days=90), today + timedelta(days=90))
    return JsonResponse({
        'status': 'success',
        'optional_days': [
            {
                'date': d['date'].strftime('%Y-%m-%d'),
                'reason': d.get('reason', ''),
                'marked_by_name': d.get('marked_by_name', ''),
            }
            for d in details
        ],
    })


@permission_required('timesheet', 'view')
def my_verifications(request: HttpRequest):
    """Verifier's weekly random allocations: pending reviews plus recent decisions."""
    if not (_is_verifier(request.user) or _can_see_all_logs(request.user)):
        return redirect('permission_denied')

    allocations = []
    if _is_verifier(request.user):
        _ensure_weekly_allocation(request.user)
        allocations = get_my_allocations(request.user.id)

    pending = [a for a in allocations if a['status'] == 'pending']
    reviewed = [a for a in allocations if a['status'] != 'pending']
    context = {
        'pending_allocations': pending,
        'reviewed_allocations': reviewed[:20],
        'is_verifier': _is_verifier(request.user),
        'show_manager_tabs': True,
        'pending_verification_count': len(pending),
        'active_tab': 'verifications',
    }
    return render(request, 'my_verifications.html', context)


@permission_required('timesheet', 'view')
def verification_detail(request: HttpRequest, allocation_id):
    """Day-by-day view of an allocated employee-week, with verify/flag actions."""
    allocation = get_allocation(allocation_id)
    if not allocation:
        messages.error(request, 'Verification record not found.')
        return redirect('my_verifications')

    is_assigned = str(request.user.id) == allocation['verifier_id']
    is_groups_head_of_employee = (
        is_group_head(request.user)
        and allocation['employee_id'] in get_group_members(str(request.user.id))
    )
    if not (is_assigned or _can_see_all_logs(request.user) or is_groups_head_of_employee):
        return redirect('permission_denied')

    can_decide = allocation['status'] == 'pending' and (
        is_assigned or is_admin(request.user) or request.user.is_superuser
    )

    profile = get_user_profile_mongo(allocation['employee_id']) or {}
    default_time_in = profile.get('time_in', '09:00')
    default_time_out = profile.get('time_out', '18:00')
    effective_date = profile.get('effective_date')

    week_start = allocation['week_start']
    week_end = allocation['week_end']
    entries_by_day = get_week_entries(allocation['employee_id'], week_start)
    optional_by_date = {
        d['date']: d
        for d in get_optional_days_detail(allocation['employee_id'], week_start, week_end)
    }
    # Days the employee was non-mandatory that week are optional even without an explicit mark.
    non_mandatory_dates = get_non_mandatory_dates(profile, week_start, week_end)

    day_rows = []
    week_total = 0.0
    week_pending = 0.0
    for offset in range(6):  # Mon..Sat; Sundays are not working days anywhere in the app
        day = week_start + timedelta(days=offset)
        day_entries = entries_by_day.get(day.strftime('%Y-%m-%d'), [])
        if day_entries:
            time_in = day_entries[0].get('time_in', default_time_in)
            time_out = day_entries[0].get('time_out', default_time_out)
        else:
            time_in = default_time_in
            time_out = default_time_out
        standard_hours = (
            datetime.strptime(time_out, '%H:%M') - datetime.strptime(time_in, '%H:%M')
        ).seconds / 3600

        day_total = sum(entry.get('hours', 0) for entry in day_entries)
        optional = optional_by_date.get(day)
        non_mandatory = day in non_mandatory_dates
        before_joining = bool(effective_date and day < effective_date)
        if optional or non_mandatory or before_joining:
            pending = 0.0
        else:
            pending = standard_hours - day_total

        day_rows.append({
            'date': day,
            'entries': day_entries,
            'standard_hours': 0 if before_joining else standard_hours,
            'total_hours': round(day_total, 2),
            'pending_hours': round(pending, 2),
            'optional': optional,
            'non_mandatory': non_mandatory and not optional,
            'before_joining': before_joining,
        })
        week_total += day_total
        week_pending += pending

    context = {
        'allocation': allocation,
        'day_rows': day_rows,
        'week_total': round(week_total, 2),
        'week_pending': round(week_pending, 2),
        'days_with_entries': sum(1 for row in day_rows if row['entries']),
        'can_decide': can_decide,
        'show_manager_tabs': True,
        'pending_verification_count': count_pending_verifications(request.user.id) if _is_verifier(request.user) else 0,
        'active_tab': 'verifications',
    }
    return render(request, 'verification_detail.html', context)


@permission_required('timesheet', 'change')
def submit_verification(request: HttpRequest):
    """Record a Verified / Flagged decision on a pending allocation."""
    if request.method != 'POST':
        return redirect('my_verifications')

    allocation_id = request.POST.get('allocation_id')
    action = request.POST.get('action')
    remarks = (request.POST.get('remarks') or '').strip()

    allocation = get_allocation(allocation_id)
    if not allocation:
        messages.error(request, 'Verification record not found.')
        return redirect('my_verifications')

    if action not in ('verified', 'flagged'):
        messages.error(request, 'Invalid verification action.')
        return redirect('verification_detail', allocation_id=allocation_id)
    if action == 'flagged' and not remarks:
        messages.error(request, 'Remarks are required when flagging a timesheet for correction.')
        return redirect('verification_detail', allocation_id=allocation_id)

    bypass = is_admin(request.user) or request.user.is_superuser
    if str(request.user.id) != allocation['verifier_id'] and not bypass:
        return redirect('permission_denied')

    if decide_allocation(allocation_id, request.user.id, action, remarks, bypass_verifier=bypass):
        outcome = 'verified' if action == 'verified' else 'flagged for correction'
        messages.success(
            request,
            f"{allocation['employee_name']}'s timesheet for the week of "
            f"{allocation['week_start'].strftime('%d-%m-%Y')} was {outcome}."
        )
    else:
        messages.warning(request, 'This timesheet was already reviewed.')
    return redirect('my_verifications')


@permission_required('timesheet', 'view')
def verification_log(request: HttpRequest):
    """Review log of verified/flagged timesheets, scoped by role."""
    if _can_see_all_logs(request.user):
        scope = None
        group_names = [g['Group_name'] for g in get_all_groups()]
    elif is_group_head(request.user):
        # Own decisions plus anything about the GH's current group members.
        scope = {'$or': [
            {'verifier_id': str(request.user.id)},
            {'employee_id': {'$in': get_group_members(str(request.user.id))}},
        ]}
        group_names = get_groups_for_head(str(request.user.id))
    else:
        return redirect('permission_denied')

    week_raw = request.GET.get('week', '')
    status = request.GET.get('status', 'decided')
    group = request.GET.get('group', '')
    employee = request.GET.get('employee', '')

    week_start = None
    if week_raw:
        try:
            anchor = datetime.strptime(week_raw, '%Y-%m-%d')
            week_start = (anchor - timedelta(days=anchor.weekday())).replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        except ValueError:
            week_raw = ''

    logs = get_verification_log(
        scope,
        week_start=week_start,
        status=status,
        group=group or None,
        employee_id=employee or None,
    )

    context = {
        'logs': logs,
        'group_names': group_names,
        'employees': get_verification_employees(scope),
        'filter_week': week_start.strftime('%Y-%m-%d') if week_start else '',
        'filter_status': status,
        'filter_group': group,
        'filter_employee': employee,
        'show_manager_tabs': True,
        'pending_verification_count': count_pending_verifications(request.user.id) if _is_verifier(request.user) else 0,
        'active_tab': 'log',
    }
    return render(request, 'verification_log.html', context)