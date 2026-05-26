import pymongo
from datetime import datetime
from bson.objectid import ObjectId
from accounts.views import get_user_name

__MONGO_CONNECTION_URI__ = 'mongodb://localhost/'

client = pymongo.MongoClient(__MONGO_CONNECTION_URI__, 27017)
db = client.HMD

def get_client_names():
    """Get all client names from clientMaster collection"""
    clients = db.clientMaster.find({}, {'Name': 1})
    return [client['Name'] for client in clients]

def save_timesheet(data):
    """Save timesheet entry to MongoDB"""
    data['created_at'] = datetime.now()
    return db.timesheetMaster.insert_one(data)

def get_user_timesheets(user_id, date=None, limit=None, id=None):
    """Get user's timesheets for a specific date"""
    query = {'user_id': str(user_id)}
    if date:
        query['date'] = date
    if limit:
        return list(db.timesheetMaster.find(query,{'_id': 0}).sort('created_at', -1).limit(limit))
    if id:
        entries = list(db.timesheetMaster.find(query).sort('created_at', -1))
        # Convert ObjectId to string for each entry
        for entry in entries:
            if '_id' in entry:
                entry['_id'] = str(entry['_id'])
        return entries
    return list(db.timesheetMaster.find(query,{'_id': 0}).sort('created_at', -1))


def get_total_hours(user_id, date):
    """Get total utilized hours for a user on a specific date"""
    pipeline = [
        {
            '$match': {
                'user_id': str(user_id),
                'date': date
            }
        },
        {
            '$group': {
                '_id': None,
                'total_hours': {'$sum': '$hours'}
            }
        }
    ]
    result = list(db.timesheetMaster.aggregate(pipeline))
    return result[0]['total_hours'] if result else 0 


def get_it_returns(client_name):
    results = list(db.returnMaster.find({'Read': {'$ne': 'Read'}, 'Name': client_name}, 
                                     {'AY': 1, 'Type': 1, 'Remarks': 1}))
    
    formatted_results = []
    for result in results:
        display_text = f"A.Y {result['AY']} + {result['Type']} + {result.get('Remarks', '')}"
        formatted_results.append({
            'id': str(result['_id']),
            'display': display_text
        })
    return formatted_results

def get_certificates(client_name):
    results = list(db.certificateMaster.find({'Read': {'$ne': 'Read'}, 'Name': client_name}, 
                                          {'Description': 1, 'Remarks': 1, 'Detailed_description': 1}))
    
    formatted_results = []
    for result in results:
        display_text = f"{result['Description']} +  {result.get('Detailed_description', '')} + {result.get('Remarks', '')}"
        formatted_results.append({
            'id': str(result['_id']),
            'display': display_text
        })
    return formatted_results

def get_other_forms(client_name):
    results = list(db.otherFormsMaster.find({'Read': {'$ne': 'Read'}, 'Name': client_name}, 
                                         {'Description': 1, 'Remarks': 1, 'Detailed_description': 1}))
    formatted_results = []
    for result in results:
        display_text = f"{result['Description']} + {result.get('Detailed_description', '')} + {result.get('Remarks', '')}"
        formatted_results.append({
            'id': str(result['_id']),
            'display': display_text
        })
    return formatted_results


def get_tds(client_name):
    results = list(db.tdsMaster.find({'Read': {'$ne': 'Read'}, 'Name': client_name}, 
                                         {'AY': 1, 'Form': 1, 'Quarter': 1, 'Type': 1}))
    formatted_results = []
    for result in results:
        display_text = f"A.Y {result['AY']} + {result.get('Form', '')} + {result.get('Quarter', '')} + {result.get('Type', '')}"
        formatted_results.append({
            'id': str(result['_id']),
            'display': display_text
        })
    return formatted_results

def get_proceedings(client_name):
    results = list(db.proceedingsMaster.find({'Read': {'$ne': 'Read'}, 'Name': client_name}, 
                                          {'Description': 1, 'Section': 1, 'Case_reference_no': 1, 
                                           'Closure_particulars': 1, 'AY': 1, 'Remarks': 1}))
    formatted_results = []
    for result in results:
        base_str = f"A.Y {result['AY']} + {result['Description']} + {result['Section']} + {result['Case_reference_no']}"
        if 'Closure_particulars' in result:
            base_str += f" + {result.get('Closure_particulars', '')}"
        if 'Remarks' in result:
            base_str += f" + {result.get('Remarks', '')}"
        formatted_results.append({
            'id': str(result['_id']),
            'display': base_str
        })
    return formatted_results
   
def delete_timesheet_entry(entry_id, user_id):
    """Delete a timesheet entry by its ID, verifying it belongs to the user"""
    try:
        # First verify the entry belongs to the user
        entry = db.timesheetMaster.find_one({'_id': ObjectId(entry_id), 'user_id': user_id})
        if not entry:
            return False
            
        # If entry exists and belongs to user, delete it
        result = db.timesheetMaster.delete_one({'_id': ObjectId(entry_id)})
        return result.deleted_count > 0
    except Exception as e:
        print(f"Error deleting timesheet entry: {e}")
        return False

def mark_leave(user_id, date):
    """Mark a day as leave for a user"""
    try:
        # Check if there are any timesheet entries for this date
        existing_entries = get_user_timesheets(user_id, date)
        if existing_entries:
            return False, "Cannot mark leave for a date with existing timesheet entries"
            
        # Check if leave is already marked
        existing_leave = db.leaveMaster.find_one({'user_id': str(user_id), 'date': date})
        if existing_leave:
            return False, "Leave is already marked for this date"
            
        # Save leave record
        db.leaveMaster.insert_one({
            'user_id': str(user_id),
            'date': date,
            'created_at': datetime.now()
        })
        return True, "Leave marked successfully"
    except Exception as e:
        return False, str(e)

def unmark_leave(user_id, date):
    """Unmark a day as leave for a user"""
    try:
        result = db.leaveMaster.delete_one({'user_id': str(user_id), 'date': date})
        if result.deleted_count > 0:
            return True, "Leave unmarked successfully"
        return False, "No leave record found for this date"
    except Exception as e:
        return False, str(e)

def is_leave(user_id, date):
    """Check if a day is marked as leave"""
    return bool(db.leaveMaster.find_one({'user_id': str(user_id), 'date': date}))


def _normalize_date(d):
    """Normalize a datetime to midnight, matching timesheetMaster.date / effective_date storage."""
    return d.replace(hour=0, minute=0, second=0, microsecond=0)


def mark_optional_days(user_id, dates, reason='', marked_by=None, marked_by_name=None):
    """Mark each date in `dates` as an optional (non-pending) timesheet day for a user.

    One document per (user_id, date); idempotent upsert so re-marking updates the reason
    instead of duplicating. Sundays are NOT filtered here - the caller expands working days.
    Returns the number of dates processed.
    """
    count = 0
    for d in dates:
        nd = _normalize_date(d)
        db.optionalDayMaster.update_one(
            {'user_id': str(user_id), 'date': nd},
            {
                '$set': {
                    'reason': (reason or '').upper(),
                    'marked_by': str(marked_by) if marked_by else None,
                    'marked_by_name': marked_by_name,
                },
                '$setOnInsert': {'created_at': datetime.now()},
            },
            upsert=True,
        )
        count += 1
    return count


def unmark_optional_days(user_id, dates):
    """Remove optional-day marks for the given dates. Returns the number deleted."""
    norm = [_normalize_date(d) for d in dates]
    result = db.optionalDayMaster.delete_many(
        {'user_id': str(user_id), 'date': {'$in': norm}}
    )
    return result.deleted_count


def get_optional_dates(user_id, start, end):
    """Return a set of normalized (midnight) datetimes marked optional in [start, end].

    Used to prefetch a user's optional days for O(1) membership checks in the pending loops.
    """
    docs = db.optionalDayMaster.find(
        {
            'user_id': str(user_id),
            'date': {'$gte': _normalize_date(start), '$lte': _normalize_date(end)},
        },
        {'_id': 0, 'date': 1},
    )
    return {doc['date'] for doc in docs}


def get_optional_days_detail(user_id, start, end):
    """Return [{date, reason, marked_by_name}] for a user's optional days in [start, end]."""
    docs = db.optionalDayMaster.find(
        {
            'user_id': str(user_id),
            'date': {'$gte': _normalize_date(start), '$lte': _normalize_date(end)},
        },
        {'_id': 0},
    ).sort('date', 1)
    return list(docs)


def get_user_timesheets_by_task_assignment(assignment_id):
    """Get users who have worked on a specific task and assignment"""
    query = {'assignment_id': str(assignment_id)}
    entries = []
    entries = list(db.timesheetMaster.find(query, {'_id': 0, 'user_id': 1, 'hours': 1, 'date': 1, 'assignment': 1}).sort('created_at', -1))
    # get user name from user_id
    for entry in entries:
        users = get_user_name(entry['user_id'])
        entry['user_name'] = users['first_name'] + ' ' + users['last_name']
        entry['designation'] = users['designation']
        entry['rate_history'] = users['rate_history']

    return entries


def get_user_first_effective_date(user_id):
    """Get user's effective date"""
    rate_history = db.userProfiles.find_one({'django_user_id': str(user_id)}, {'_id': 0, 'effective_date': 1, 'rate_history': 1})
    if rate_history:
        return rate_history['rate_history'][-1]['effective_date']
    return rate_history['effective_date']
