from django.contrib.auth.decorators import user_passes_test
from functools import wraps
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.urls import reverse

def permission_required(app_name, permission_type):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Check if user is authenticated
            if not request.user.is_authenticated:
                return redirect(f"{reverse('login')}?next={request.path}")
            
            # Allow superusers full access
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
                
            # Check specific permission
            permission_codename = f'{permission_type}_{app_name.lower()}'
            if request.user.has_perm(f'{app_name.lower()}.{permission_codename}'):
                return view_func(request, *args, **kwargs)
            
            # If permission check fails, redirect to permission denied page
            return redirect('permission_denied')
        return _wrapped_view
    return decorator 
