from django.db import migrations

def migrate_user_data_to_mongo(apps, schema_editor):
    """
    Migrate existing user profile data to MongoDB
    """
    UserProfile = apps.get_model('accounts', 'UserProfile')
    from accounts.database import create_user_profile_mongo
    
    for profile in UserProfile.objects.all():
        try:
            # Get all the data from the old profile
            profile_data = {
                'user': profile.user,
                'area': getattr(profile, 'area', ''),
                'group': getattr(profile, 'group', ''),
                'designation': getattr(profile, 'designation', ''),
                'time_in': getattr(profile, 'time_in', None),
                'time_out': getattr(profile, 'time_out', None),
                'effective_date': getattr(profile, 'effective_date', None),
                'rate_card': getattr(profile, 'rate_card', False),
                'hourly_rate': getattr(profile, 'hourly_rate', None)
            }
            # Create MongoDB profile
            create_user_profile_mongo(profile_data)
        except Exception as e:
            print(f"Error migrating user {profile.user.username}: {str(e)}")

def reverse_migrate(apps, schema_editor):
    """
    Reverse migration - optional but recommended
    """
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0005_auto_20250201_0157'),  # Replace with your actual latest migration name
    ]

    operations = [
        migrations.RunPython(migrate_user_data_to_mongo, reverse_migrate),
    ]