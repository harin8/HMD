from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib import messages
from django.urls import reverse
from accounts.database import delete_user_profile_mongo,get_all_groups, create_user_profile_mongo, get_user_profile_mongo, update_user_profile_mongo, create_group_head_assignments, update_group_head_assignments, remove_group_head_assignments, set_timesheet_mandatory, is_timesheet_mandatory, set_user_status, get_user_status
from datetime import datetime
from django.conf import settings
from accounts.roles import ROLE_PERMISSIONS
from accounts.decorators import permission_required

def is_superuser(user):
    return user.is_superuser


def _apply_status_change(request, user_id, new_status, prev_status, prev_status_effective, user_start):
    """Record an account-status change; on return to Active, excuse the away period.

    When a user comes back from Hold/Inactive, the days they were away are marked
    optional (reusing the timesheet optional-day mechanism) so they never show as
    pending/critical. Returns True if the status actually changed.
    """
    changed, _ = set_user_status(user_id, new_status, request.user.id, request.user.get_full_name())
    if changed and new_status == 'active' and prev_status in ('hold', 'inactive'):
        from timesheet.database import mark_period_optional
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start = prev_status_effective or user_start or settings.TIMESHEET_START_DATE
        reason = 'ON HOLD' if prev_status == 'hold' else 'INACTIVE PERIOD'
        mark_period_optional(
            user_id, start, today, reason=reason,
            marked_by=request.user.id, marked_by_name=request.user.get_full_name(),
        )
    return changed

@ensure_csrf_cookie
def login_view(request):
    # Store the next parameter if it exists
    next_url = request.GET.get('next', 'Landing')
    
    if request.user.is_authenticated:
        return redirect(next_url)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(next_url)
        else:
            return render(request, 'accounts/login.html', {
                'error': 'Invalid credentials',
                'next': next_url
            })
    
    return render(request, 'accounts/login.html', {'next': next_url})

@permission_required('accounts', 'view')
def user_management(request):
    # Get all users except the current user
    users = User.objects.all().exclude(id=request.user.id)
    
    # Attach MongoDB profiles to users, with an effective status for legacy profiles.
    for user in users:
        profile = get_user_profile_mongo(user.id)
        if profile is not None:
            profile['status'] = profile.get('status') or ('active' if user.is_active else 'inactive')
        user.mongo_profile = profile

    return render(request, 'accounts/user_management.html', {'users': users})


@permission_required('accounts', 'add')
def create_user(request):
    if request.method == 'POST':
        username = request.POST.get('username').upper()
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name').upper()
        last_name = request.POST.get('last_name').upper()
        role = request.POST.get('role')
        status = request.POST.get('status', 'active')
        is_active = status == 'active'

        try:
            # Create Django user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                is_active=is_active
            )

            # Set superuser status if role is Super Admin
            if role == 'Super Admin':
                user.is_superuser = True
                user.is_staff = True
                user.save()

            # Assign user to the role group
            role_group = Group.objects.get(name=role)
            user.groups.add(role_group)

            # Handle multiple groups
            groups = request.POST.getlist('groups[]')
            
            # If user is a Group Head, update the groupHead collection
            if role == 'Group Head':
                create_group_head_assignments(user.id, groups)

            # Create MongoDB profile with rate history
            effective_date = datetime.strptime(request.POST.get('effective_date'), '%Y-%m-%d')
            hourly_rate = request.POST.get('hourly_rate')
            timesheet_mandatory = request.POST.get('timesheet_mandatory') == 'on'

            profile_data = {
                'user': user,
                'area': request.POST.get('area', '').upper(),
                'groups': groups,
                'designation': request.POST.get('designation', '').upper(),
                'role': role,
                'timesheet_mandatory': timesheet_mandatory,
                'status': status,
                'changed_by': request.user.id,
                'changed_by_name': request.user.get_full_name(),
                'time_in': request.POST.get('time_in'),
                'time_out': request.POST.get('time_out'),
                'effective_date': effective_date,
                'hourly_rate': float(hourly_rate) if hourly_rate else None,
                'rate_history': [{
                    'hourly_rate': float(hourly_rate),
                    'effective_date': effective_date,
                }] if hourly_rate else []
            }
            create_user_profile_mongo(profile_data)

            # New user starting as non-mandatory: mark their timesheets optional from day one.
            if not timesheet_mandatory:
                from timesheet.database import mark_period_optional
                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                mark_period_optional(
                    user.id, effective_date, today,
                    reason='TIMESHEET NOT MANDATORY',
                    marked_by=request.user.id, marked_by_name=request.user.get_full_name(),
                )

            messages.success(request, f'User {username} has been created successfully.')
            return JsonResponse({'status': 'success', 'redirect_url': reverse('user_management')})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    # GET request - render the create user form
    return render(request, 'accounts/create_user.html', {
        'groups': get_all_groups(),
        'roles': list(ROLE_PERMISSIONS.keys())
    })

@permission_required('accounts', 'change')
def edit_user(request, user_id):
    editing_user = get_object_or_404(User, id=user_id)
    mongo_profile = get_user_profile_mongo(user_id)
    
    if request.method == 'POST':
        try:
            # Update Django user
            editing_user.username = request.POST.get('username').upper()
            editing_user.email = request.POST.get('email')
            editing_user.first_name = request.POST.get('first_name').upper()
            editing_user.last_name = request.POST.get('last_name').upper()
            # Account status drives Django's is_active (active -> can log in).
            new_status = request.POST.get('status', 'active')
            if new_status not in ('active', 'hold', 'inactive'):
                new_status = 'active'
            prev_status = get_user_status(mongo_profile)
            prev_status_effective = None
            if mongo_profile and mongo_profile.get('status_history'):
                prev_status_effective = mongo_profile['status_history'][0].get('effective_date')
            editing_user.is_active = new_status == 'active'

            # Handle password change if provided
            if request.POST.get('password'):
                editing_user.set_password(request.POST.get('password'))
            
            # Handle role change
            new_role = request.POST.get('role')
            old_role = next((group.name for group in editing_user.groups.all()), None)
            
            # Remove user from all existing groups
            editing_user.groups.clear()
            
            # Add user to new role group
            role_group = Group.objects.get(name=new_role)
            editing_user.groups.add(role_group)
            
            # Handle multiple groups
            new_groups = request.POST.getlist('groups[]')
            old_groups = mongo_profile.get('groups', []) if mongo_profile else []

            # Handle Group Head role changes
            if new_role == 'Group Head':
                update_group_head_assignments(user_id, new_groups, old_groups)
            elif old_role == 'Group Head':
                remove_group_head_assignments(user_id)

            # Set superuser status if role is Super Admin
            editing_user.is_superuser = (new_role == 'Super Admin')
            editing_user.is_staff = (new_role == 'Super Admin')
            
            editing_user.save()

            # Prepare MongoDB profile data
            effective_date_str = request.POST.get('effective_date')
            effective_date = datetime.strptime(effective_date_str, '%Y-%m-%d') if effective_date_str else None
            hourly_rate = request.POST.get('hourly_rate')

            # Handle multiple groups
            groups = request.POST.getlist('groups[]')
            
            profile_data = {
                'area': request.POST.get('area', '').upper(),
                'groups': groups,  # Store as array
                'designation': request.POST.get('designation', '').upper(),
                'role': new_role,
                'time_in': request.POST.get('time_in'),
                'time_out': request.POST.get('time_out'),
            }

            # Only add rate-related fields if they are provided
            if effective_date:
                profile_data['effective_date'] = effective_date
            if hourly_rate:
                profile_data['hourly_rate'] = float(hourly_rate)

            # Handle rate history - only if both fields are provided
            if hourly_rate and effective_date:
                rate_history = mongo_profile.get('rate_history', []) if mongo_profile else []
                
                new_rate_entry = {
                    'hourly_rate': float(hourly_rate),
                    'effective_date': effective_date,
                    'created_at': datetime.now()
                }
                
                # Only add if it's different from the latest entry
                if not rate_history or \
                   rate_history[0]['hourly_rate'] != float(hourly_rate) or \
                   rate_history[0]['effective_date'].date() != effective_date.date():
                    rate_history.insert(0, new_rate_entry)
                    profile_data['rate_history'] = rate_history

            # Update MongoDB profile
            update_user_profile_mongo(user_id, profile_data)

            # Timesheet-mandatory toggle + audit history (kept separate so update_user_profile_mongo
            # doesn't clobber the mandatory fields).
            timesheet_mandatory = request.POST.get('timesheet_mandatory') == 'on'
            changed = set_timesheet_mandatory(
                user_id, timesheet_mandatory, request.user.id, request.user.get_full_name()
            )
            # Switched off: retroactively mark every working day from the user's start optional.
            if changed and not timesheet_mandatory:
                from timesheet.database import mark_period_optional
                start = effective_date or (mongo_profile.get('effective_date') if mongo_profile else None) or settings.TIMESHEET_START_DATE
                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                mark_period_optional(
                    user_id, start, today,
                    reason='TIMESHEET NOT MANDATORY',
                    marked_by=request.user.id, marked_by_name=request.user.get_full_name(),
                )

            # Account status toggle + audit history.
            _apply_status_change(
                request, user_id, new_status, prev_status, prev_status_effective,
                effective_date or (mongo_profile.get('effective_date') if mongo_profile else None),
            )

            messages.success(request, f'User {editing_user.username} has been updated successfully.')
            return redirect('user_management')
            
        except Exception as e:
            messages.error(request, f'Error updating user: {str(e)}')
            return redirect('edit_user', user_id=user_id)
    
    # Prepare context for GET request
    user_data = {
        'id': editing_user.id,
        'username': editing_user.username,
        'email': editing_user.email,
        'first_name': editing_user.first_name,
        'last_name': editing_user.last_name,
        'is_active': editing_user.is_active,
        'role': next((group.name for group in editing_user.groups.all()), None)
    }

    # Add MongoDB profile data if it exists
    if mongo_profile:
        user_data.update({
            'area': mongo_profile.get('area', ''),
            'groups': mongo_profile.get('groups', []),  # Get as array
            'designation': mongo_profile.get('designation', ''),
            'time_in': mongo_profile.get('time_in', ''),
            'time_out': mongo_profile.get('time_out', ''),
            'effective_date': mongo_profile.get('effective_date'),
            'hourly_rate': mongo_profile.get('hourly_rate'),
            'timesheet_mandatory': is_timesheet_mandatory(mongo_profile),
            'mandatory_history': mongo_profile.get('mandatory_history', []),  # already newest-first
            'status': get_user_status(mongo_profile) if mongo_profile.get('status') else ('active' if editing_user.is_active else 'inactive'),
            'status_history': mongo_profile.get('status_history', []),  # already newest-first
            'rate_history': sorted(
                mongo_profile.get('rate_history', []),
                key=lambda x: x['effective_date'],
                reverse=True
            )
        })
    else:
        user_data['timesheet_mandatory'] = True
        user_data['status'] = 'active' if editing_user.is_active else 'inactive'
    
    context = {
        'edit_user': editing_user,
        'user_profile': user_data,
        'groups': get_all_groups(),
        'roles': list(ROLE_PERMISSIONS.keys()),
        'is_editing_superuser': editing_user.is_superuser and editing_user != request.user
    }
    
    return render(request, 'accounts/edit_user.html', context)

def permission_denied(request):
    # Get the user's current roles/groups
    user_groups = request.user.groups.all()
    user_permissions = request.user.get_all_permissions()
    
    context = {
        'user': request.user,
        'groups': user_groups,
        'permissions': user_permissions,
    }
    
    return render(request, 'accounts/permission_denied.html', context)

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')


def accounts_landing(request):
    return render(request, 'accounts/accounts_landing.html')


def get_user_name(user_id):
    users = User.objects.get(id=user_id)
    profile = get_user_profile_mongo(user_id)
    designation = profile.get('designation', '')
    rate_history = profile.get('rate_history', [])

    #return object with user_name and designation
    return {'first_name': users.first_name, 'last_name': users.last_name, 'designation': designation, 'rate_history': rate_history}
    

