import pymongo
from datetime import datetime
from django.contrib.auth.models import User

__MONGO_CONNECTION_URI__ = 'mongodb://localhost/'

client = pymongo.MongoClient(__MONGO_CONNECTION_URI__, 27017)
db = client.HMD

def get_all_groups():
    """Get all groups from groupCode collection"""
    group_doc = db.groupCode.find_one({}, {'_id': 0})  # Exclude _id field
    if group_doc:
        # Convert the document into a list of group names
        # Skip the _id field and sort by numeric key
        groups = []
        for key in sorted(group_doc.keys(), key=lambda x: int(x) if x.isdigit() else float('inf')):
            if key.isdigit():  # Only process numeric keys
                groups.append({'Group_name': group_doc[key]})
        return groups
    return [] 

def create_user_profile_mongo(user_data):
    """Create user profile in MongoDB"""
    profile_data = {
        "django_user_id": str(user_data['user'].id),
        "area": user_data.get('area', ''),
        "groups": user_data.get('groups', []),  # Store as array
        "designation": user_data.get('designation', ''),
        "role": user_data.get('role', ''),
        "time_in": user_data.get('time_in'),
        "time_out": user_data.get('time_out'),
        "effective_date": user_data.get('effective_date'),
        "hourly_rate": float(user_data.get('hourly_rate', 0)) if user_data.get('hourly_rate') else None,
        "rate_history": user_data.get('rate_history', []),
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    return db.userProfiles.insert_one(profile_data)

def get_user_profile_mongo(django_user_id):
    """Get user profile from MongoDB"""
    profile = db.userProfiles.find_one({"django_user_id": str(django_user_id)})
    
    # Convert MongoDB date objects to Python datetime
    if profile and profile.get('rate_history'):
        for rate in profile['rate_history']:
            if isinstance(rate['effective_date'], str):
                rate['effective_date'] = datetime.strptime(rate['effective_date'], '%Y-%m-%d')
    
    return profile

def update_user_profile_mongo(django_user_id, update_data):
    """Update user profile in MongoDB"""
    current_profile = get_user_profile_mongo(django_user_id)
    
    profile_data = {
        "area": update_data.get('area'),
        "groups": update_data.get('groups', []),  # Store as array
        "designation": update_data.get('designation'),
        "role": update_data.get('role'),
        "time_in": update_data.get('time_in'),
        "time_out": update_data.get('time_out'),
        "effective_date": update_data.get('effective_date'),
        "updated_at": datetime.now()
    }
    
    # Handle rate history
    if update_data.get('hourly_rate'):
        new_rate = {
            "hourly_rate": float(update_data['hourly_rate']),
            "effective_date": update_data['effective_date'],
            "created_at": datetime.now()
        }
        
        if not current_profile.get('rate_history'):
            profile_data['rate_history'] = [new_rate]
        else:
            rate_history = current_profile['rate_history']
            # Only add if rate or date is different from the latest entry
            if not rate_history or \
               rate_history[0]['hourly_rate'] != float(update_data['hourly_rate']) or \
               rate_history[0]['effective_date'] != update_data['effective_date']:
                rate_history.insert(0, new_rate)
                profile_data['rate_history'] = rate_history
    
    return db.userProfiles.update_one(
        {"django_user_id": str(django_user_id)},
        {"$set": profile_data}
    )

def delete_user_profile_mongo(django_user_id):
    """Delete user profile from MongoDB"""
    return db.userProfiles.delete_one({"django_user_id": str(django_user_id)})

def get_group_heads(group_name):
    """Get all group heads for a specific group"""
    group_head_entry = db.groupHead.find_one({'group': group_name})
    if group_head_entry and 'django_user_ids' in group_head_entry:
        return User.objects.filter(id__in=group_head_entry['django_user_ids'])
    return []

def get_groups_for_head(user_id):
    """Get all groups where user is a head"""
    groups = db.groupHead.find({'django_user_ids': str(user_id)})
    return [group['group'] for group in groups]

def is_group_head_for(user_id, group_name):
    """Check if user is a head for specific group"""
    group_head_entry = db.groupHead.find_one({
        'group': group_name,
        'django_user_ids': str(user_id)
    })
    return bool(group_head_entry)

def update_group_head_assignments(user_id, new_groups, old_groups=None, is_new_group_head=False, remove_all=False):
    """
    Update group head assignments in MongoDB
    
    Parameters:
    - user_id: str, the Django user ID
    - new_groups: list, new groups to assign
    - old_groups: list, previous groups (for editing)
    - is_new_group_head: bool, whether this is a new group head
    - remove_all: bool, whether to remove user from all group head assignments
    """
    try:
        if remove_all:
            # Remove user from all group head assignments
            db.groupHead.update_many(
                {'django_user_ids': str(user_id)},
                {
                    '$pull': {'django_user_ids': str(user_id)},
                    '$set': {'updated_at': datetime.now()}
                }
            )
            return True

        # Add user to new group assignments
        for group in new_groups:
            db.groupHead.update_one(
                {'group': group},
                {
                    '$addToSet': {'django_user_ids': str(user_id)},
                    '$set': {'updated_at': datetime.now()}
                },
                upsert=True
            )

        # If editing existing group head, remove from old groups
        if not is_new_group_head and old_groups:
            groups_to_remove = set(old_groups) - set(new_groups)
            for group in groups_to_remove:
                db.groupHead.update_one(
                    {'group': group},
                    {
                        '$pull': {'django_user_ids': str(user_id)},
                        '$set': {'updated_at': datetime.now()}
                    }
                )

        return True

    except Exception as e:
        print(f"Error updating group head assignments: {str(e)}")
        return False

def create_group_head_assignments(user_id, groups):
    """Create new group head assignments"""
    return update_group_head_assignments(
        user_id=user_id,
        new_groups=groups,
        is_new_group_head=True
    )

def remove_group_head_assignments(user_id):
    """Remove all group head assignments for a user"""
    return update_group_head_assignments(
        user_id=user_id,
        new_groups=[],
        remove_all=True
    )

def get_group_members(user_id):
    """
    Get all senior staff and trainee user IDs that belong to the same groups as the group head
    
    Parameters:
    - user_id: str, the Django user ID of the group head
    
    Returns:
    - list of user IDs who are members of the group head's groups
    """
    try:
        # First get all groups where this user is a head
        head_groups = get_groups_for_head(user_id)
        
        if not head_groups:
            return []
        
        # Find all user profiles that have any of these groups
        # and are not group heads themselves
        member_profiles = db.userProfiles.find({
            'groups': {'$in': head_groups},
            'role': {'$in': ['Senior Staff', 'Trainee']}
        })
        
        # Extract Django user IDs from the profiles
        member_ids = [profile['django_user_id'] for profile in member_profiles]
        
        return member_ids
        
    except Exception as e:
        print(f"Error fetching group members: {str(e)}")
        return [] 