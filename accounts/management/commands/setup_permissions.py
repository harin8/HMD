from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from accounts.roles import ROLE_PERMISSIONS, APP_PERMISSIONS

class Command(BaseCommand):
    help = 'Set up initial groups and permissions'

    def handle(self, *args, **options):
        # Clear existing permissions
        Permission.objects.all().delete()
        self.stdout.write('Cleared existing permissions')

        # Create content types for each app
        for app_name in APP_PERMISSIONS:
            content_type, _ = ContentType.objects.get_or_create(
                app_label=app_name.lower(),
                model='appaccess'
            )
            
            # Create permissions for this app
            for permission_type in APP_PERMISSIONS[app_name]:
                permission, created = Permission.objects.get_or_create(
                    codename=f'{permission_type}_{app_name.lower()}',
                    name=f'Can {permission_type} {app_name}',
                    content_type=content_type,
                )
                if created:
                    self.stdout.write(f'Created permission: {permission.name}')

        # Create groups and assign permissions
        for role_name, role_config in ROLE_PERMISSIONS.items():
            group, created = Group.objects.get_or_create(name=role_name)
            if created:
                self.stdout.write(f'Created group: {role_name}')
            
            # Clear existing permissions
            group.permissions.clear()
            
            # Assign new permissions
            for app_name, permissions in role_config['apps'].items():
                content_type = ContentType.objects.get(
                    app_label=app_name.lower(),
                    model='appaccess'
                )
                
                for permission_type in permissions:
                    permission = Permission.objects.get(
                        codename=f'{permission_type}_{app_name.lower()}',
                        content_type=content_type,
                    )
                    group.permissions.add(permission)
                    self.stdout.write(f'Added {permission.name} to {role_name}')

        self.stdout.write(self.style.SUCCESS('Successfully set up all permissions')) 