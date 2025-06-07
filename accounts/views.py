from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib import messages
from django.urls import reverse
from accounts.database import delete_user_profile_mongo,get_all_groups, create_user_profile_mongo, get_user_profile_mongo, update_user_profile_mongo, create_group_head_assignments, update_group_head_assignments, remove_group_head_assignments
from datetime import datetime
from accounts.roles import ROLE_PERMISSIONS
from accounts.decorators import permission_required

def is_superuser(user):
    return user.is_superuser

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
    # Get all users except the current user and not active user
    users = User.objects.filter(is_active=True).exclude(id=request.user.id)
    
    # Attach MongoDB profiles to users
    for user in users:
        user.mongo_profile = get_user_profile_mongo(user.id)
    
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
        is_active = request.POST.get('is_active', 'on') == 'on'

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
            
            profile_data = {
                'user': user,
                'area': request.POST.get('area', '').upper(),
                'groups': groups,
                'designation': request.POST.get('designation', '').upper(),
                'role': role,
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
            editing_user.is_active = request.POST.get('is_active') == 'on'
            
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
            'rate_history': sorted(
                mongo_profile.get('rate_history', []),
                key=lambda x: x['effective_date'],
                reverse=True
            )
        })
    
    context = {
        'edit_user': editing_user,
        'user_profile': user_data,
        'groups': get_all_groups(),
        'roles': list(ROLE_PERMISSIONS.keys()),
        'is_editing_superuser': editing_user.is_superuser and editing_user != request.user
    }
    
    return render(request, 'accounts/edit_user.html', context)

@permission_required('accounts', 'delete')
def delete_user(request, user_id):
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method'
        }, status=405)

    try:
        # Get the user to delete
        user_to_delete = User.objects.get(id=user_id)
        # Prevent superuser from being deleted
        if user_to_delete.is_superuser:
            return JsonResponse({
                'status': 'error',
                'message': 'Cannot delete superuser account'
            }, status=403)

        # Verify the current user's password
        password = request.POST.get('password')
        if not request.user.check_password(password):
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid password'
            }, status=403)

        # Delete the user
        user_to_delete.delete()

        #delete the user from the mongo db
        delete_user_profile_mongo(user_id)

        return JsonResponse({
            'status': 'success',
            'message': 'User deleted successfully'
        })

    except User.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'User not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

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
    

