import pymongo
from datetime import datetime, timedelta
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
    role = user_data.get('role', '')
    # Explicit choice from the form wins; otherwise fall back to the role default.
    timesheet_mandatory = user_data.get('timesheet_mandatory')
    if timesheet_mandatory is None:
        timesheet_mandatory = role not in ['Super Admin', 'Super Group Head', 'Group Head']

    effective_date = user_data.get('effective_date')
    profile_data = {
        "django_user_id": str(user_data['user'].id),
        "area": user_data.get('area', ''),
        "groups": user_data.get('groups', []),  # Store as array
        "designation": user_data.get('designation', ''),
        "role": role,
        "timesheet_mandatory": timesheet_mandatory,
        # Audit log of mandatory toggles, mirroring rate_history (newest at index 0).
        "mandatory_history": [{
            "mandatory": timesheet_mandatory,
            "effective_date": effective_date or datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
            "changed_by": user_data.get('changed_by'),
            "changed_by_name": user_data.get('changed_by_name'),
            "created_at": datetime.now(),
        }],
        # Account status: 'active' | 'hold' | 'inactive' (Django is_active == status=='active').
        "status": user_data.get('status', 'active'),
        "status_history": [{
            "status": user_data.get('status', 'active'),
            "effective_date": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
            "changed_by": user_data.get('changed_by'),
            "changed_by_name": user_data.get('changed_by_name'),
            "created_at": datetime.now(),
        }],
        "time_in": user_data.get('time_in'),
        "time_out": user_data.get('time_out'),
        "effective_date": effective_date,
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

def get_users_by_role(role):
    """Return django_user_ids of all userProfiles with the given role (e.g. 'Group Head')."""
    profiles = db.userProfiles.find({'role': role}, {'_id': 0, 'django_user_id': 1})
    return [profile['django_user_id'] for profile in profiles]

def is_timesheet_mandatory(user_profile):
    """Check if timesheet is mandatory for a user based on profile or default role logic."""
    if 'timesheet_mandatory' in user_profile:
        return user_profile['timesheet_mandatory']
    # Fallback default if field missing
    role = user_profile.get('role', '')
    return role not in ['Super Admin', 'Super Group Head', 'Group Head']

def update_timesheet_mandatory_status(django_user_id, status: bool):
    """Update timesheet mandatory status in MongoDB (boolean only, no history).

    Prefer set_timesheet_mandatory() which also records the change in mandatory_history.
    """
    return db.userProfiles.update_one(
        {"django_user_id": str(django_user_id)},
        {"$set": {"timesheet_mandatory": status, "updated_at": datetime.now()}}
    )


def _normalize_day(d):
    """Midnight datetime, matching how timesheet dates / effective_date are stored."""
    return d.replace(hour=0, minute=0, second=0, microsecond=0)


def _mandatory_on(history, day):
    """Whether the timesheet was mandatory on `day` per a newest-first mandatory_history.

    Returns the status of the most recent entry whose effective_date <= day; for days
    before the earliest entry, falls back to the earliest entry's status (or True).
    """
    if not history:
        return True
    day = _normalize_day(day)
    for entry in history:  # newest first
        eff = entry.get('effective_date')
        if eff and _normalize_day(eff) <= day:
            return entry.get('mandatory', True)
    return history[-1].get('mandatory', True)


def get_non_mandatory_dates(profile, start, end):
    """Set of working-day (Mon-Sat) midnights in [start, end] that fell in a non-mandatory period.

    Driven by the user's mandatory_history; empty when the user has no history (so callers
    fall back to plain optional-day handling). Lets the timesheet views treat non-mandatory
    stretches as optional without stamping every future day.
    """
    history = profile.get('mandatory_history') if profile else None
    if not history:
        return set()
    cur = _normalize_day(start)
    end = _normalize_day(end)
    result = set()
    while cur <= end:
        if cur.weekday() != 6 and not _mandatory_on(history, cur):  # skip Sundays
            result.add(cur)
        cur += timedelta(days=1)
    return result


def set_timesheet_mandatory(django_user_id, mandatory, changed_by=None, changed_by_name=None):
    """Set a user's timesheet-mandatory status, appending to mandatory_history when it changes.

    Mirrors the rate_history idiom: a new entry is inserted at index 0 only when the value
    differs from the current head. Keeps the denormalized timesheet_mandatory boolean in sync.
    Returns True if the status actually changed.
    """
    profile = get_user_profile_mongo(django_user_id)
    history = (profile.get('mandatory_history', []) if profile else []) or []

    changed = not history or history[0].get('mandatory') != mandatory
    if changed:
        history.insert(0, {
            "mandatory": mandatory,
            "effective_date": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
            "changed_by": str(changed_by) if changed_by else None,
            "changed_by_name": changed_by_name,
            "created_at": datetime.now(),
        })

    db.userProfiles.update_one(
        {"django_user_id": str(django_user_id)},
        {"$set": {
            "timesheet_mandatory": mandatory,
            "mandatory_history": history,
            "updated_at": datetime.now(),
        }},
    )
    return changed


def get_user_status(profile):
    """Effective account status of a profile: 'active' | 'hold' | 'inactive'.

    Falls back for legacy profiles that predate the status field.
    """
    if profile and profile.get('status'):
        return profile['status']
    return 'active'


def set_user_status(django_user_id, status, changed_by=None, changed_by_name=None):
    """Set a user's account status, appending to status_history when it changes.

    Mirrors the mandatory_history idiom (newest entry at index 0, only on change).
    Updates the Mongo profile only; the caller flips the Django User.is_active flag.
    Returns (changed, prev_status).
    """
    profile = get_user_profile_mongo(django_user_id)
    history = (profile.get('status_history', []) if profile else []) or []
    prev_status = history[0].get('status') if history else (profile.get('status') if profile else None)

    changed = prev_status != status
    if changed:
        history.insert(0, {
            "status": status,
            "effective_date": datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
            "changed_by": str(changed_by) if changed_by else None,
            "changed_by_name": changed_by_name,
            "created_at": datetime.now(),
        })

    db.userProfiles.update_one(
        {"django_user_id": str(django_user_id)},
        {"$set": {
            "status": status,
            "status_history": history,
            "updated_at": datetime.now(),
        }},
    )
    return changed, prev_status