from django.shortcuts import redirect
from django.urls import reverse, resolve
from django.conf import settings
from django.apps import apps

class PermissionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_urls = [
            reverse('login'),
            reverse('logout'),
            reverse('permission_denied'),
            '/static/',
            '/media/',
        ]

    def __call__(self, request):
        # Skip middleware for exempt URLs
        if any(request.path.startswith(url) for url in self.exempt_urls):
            return self.get_response(request)

        # Check if user is authenticated
        if not request.user.is_authenticated:
            return redirect(f"{reverse('login')}?next={request.path}")

        # Allow superusers full access
        if request.user.is_superuser:
            return self.get_response(request)

        try:
            # Get the resolved view function
            resolved = resolve(request.path)
            # Get the app config from the view module
            module_path = resolved.func.__module__
            app_label = module_path.split('.')[0]
            app_config = apps.get_app_config(app_label).lower()
            if app_config and app_config.name != 'django':
                # Check if user has permission for the current app
                view_permission = f'{app_config.label}.view_{app_config.label}'
                if not request.user.has_perm(view_permission):
                    return redirect('permission_denied')
        except Exception as e:
            # Log the error if needed
            # If we can't resolve the view or determine the app, let it through
            pass

        return self.get_response(request)