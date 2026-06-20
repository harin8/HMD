import pymongo
from pymongo.errors import BulkWriteError, PyMongoError
from datetime import datetime, timedelta
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


def mark_period_optional(user_id, start, end, reason='', marked_by=None, marked_by_name=None):
    """Mark every working day (Mon-Sat) in [start, end] optional via optionalDayMaster.

    One-time retroactive cleanup used when an admin flips a user to non-mandatory, so their
    accumulated past pending days stop counting. Reuses the idempotent mark_optional_days upsert.
    Returns the number of days processed.
    """
    cur = _normalize_date(start)
    end = _normalize_date(end)
    dates = []
    while cur <= end:
        if cur.weekday() != 6:  # skip Sundays
            dates.append(cur)
        cur += timedelta(days=1)
    if not dates:
        return 0
    return mark_optional_days(
        user_id, dates, reason=reason, marked_by=marked_by, marked_by_name=marked_by_name
    )


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


# ---------------------------------------------------------------------------
# Random weekly timesheet verification (timesheetVerificationMaster)
# One document per (verifier, employee, week_start); week_start is the Monday
# of the reviewed Mon-Sat week, normalized to midnight like timesheetMaster.date.
# ---------------------------------------------------------------------------

try:
    # Unique index makes lazy allocation race-safe: if two requests generate the
    # same week concurrently, the loser's duplicates are skipped (see
    # create_allocations). Wrapped so the app still imports when Mongo is down.
    db.timesheetVerificationMaster.create_index(
        [('verifier_id', 1), ('employee_id', 1), ('week_start', 1)],
        unique=True,
    )
except PyMongoError:
    pass


def has_allocations(verifier_id, week_start):
    """Check whether the verifier already has allocations for the given week."""
    return db.timesheetVerificationMaster.count_documents(
        {'verifier_id': str(verifier_id), 'week_start': _normalize_date(week_start)},
        limit=1,
    ) > 0


def get_last_allocation_map(verifier_id, employee_ids):
    """Return {employee_id: most recent week_start} this verifier was allocated them.

    Used to prefer least-recently-reviewed employees when sampling a new week.
    """
    pipeline = [
        {'$match': {
            'verifier_id': str(verifier_id),
            'employee_id': {'$in': [str(e) for e in employee_ids]},
        }},
        {'$group': {'_id': '$employee_id', 'last_week': {'$max': '$week_start'}}},
    ]
    return {doc['_id']: doc['last_week']
            for doc in db.timesheetVerificationMaster.aggregate(pipeline)}


def create_allocations(docs):
    """Insert pending allocation docs; duplicates on (verifier, employee, week) are skipped."""
    if not docs:
        return 0
    now = datetime.now()
    for doc in docs:
        doc.setdefault('status', 'pending')
        doc.setdefault('remarks', '')
        doc.setdefault('verified_at', None)
        doc.setdefault('allocated_at', now)
    try:
        result = db.timesheetVerificationMaster.insert_many(docs, ordered=False)
        return len(result.inserted_ids)
    except BulkWriteError:
        # Concurrent generation (e.g. two tabs) raced us; the unique index
        # already holds the winner's docs, so there is nothing left to do.
        return 0


def get_my_allocations(verifier_id):
    """Return all allocation docs for a verifier: pending first, newest week first.

    _id is exposed as a plain 'id' string because Django templates reject
    leading-underscore attributes.
    """
    docs = list(db.timesheetVerificationMaster.find({'verifier_id': str(verifier_id)}))
    for doc in docs:
        doc['id'] = str(doc.pop('_id'))
    docs.sort(key=lambda d: (d.get('status') != 'pending', -d['week_start'].timestamp()))
    return docs


def count_pending_verifications(verifier_id):
    """Number of allocations still awaiting this verifier's review."""
    return db.timesheetVerificationMaster.count_documents(
        {'verifier_id': str(verifier_id), 'status': 'pending'}
    )


def get_allocation(allocation_id):
    """Fetch one allocation doc by its string _id, or None if missing/invalid."""
    try:
        doc = db.timesheetVerificationMaster.find_one({'_id': ObjectId(allocation_id)})
    except Exception:
        return None
    if doc:
        doc['id'] = str(doc.pop('_id'))
    return doc


def decide_allocation(allocation_id, verifier_id, status, remarks='', bypass_verifier=False):
    """Record a verified/flagged decision on a still-pending allocation.

    Only flips docs whose status is 'pending'; returns False when the doc was
    already decided (stale tab) or belongs to another verifier (unless bypassed).
    """
    try:
        query = {'_id': ObjectId(allocation_id), 'status': 'pending'}
    except Exception:
        return False
    if not bypass_verifier:
        query['verifier_id'] = str(verifier_id)
    result = db.timesheetVerificationMaster.update_one(
        query,
        {'$set': {
            'status': status,
            'remarks': (remarks or '').upper(),
            'verified_at': datetime.now(),
        }},
    )
    return result.modified_count > 0


def get_verification_log(scope_query=None, week_start=None, status=None, group=None, employee_id=None):
    """Allocations for the log tab, newest week first.

    scope_query restricts visibility (e.g. a Group Head's own groups); status
    'decided' means verified+flagged, 'all' disables the status filter.
    """
    clauses = []
    if scope_query:
        clauses.append(scope_query)
    if week_start:
        clauses.append({'week_start': _normalize_date(week_start)})
    if status == 'decided':
        clauses.append({'status': {'$in': ['verified', 'flagged']}})
    elif status and status != 'all':
        clauses.append({'status': status})
    if group:
        clauses.append({'groups': group})
    if employee_id:
        clauses.append({'employee_id': str(employee_id)})
    query = {'$and': clauses} if clauses else {}
    docs = list(db.timesheetVerificationMaster.find(query)
                .sort([('week_start', -1), ('verified_at', -1)]))
    for doc in docs:
        doc['id'] = str(doc.pop('_id'))
    return docs


def get_verification_employees(scope_query=None):
    """Distinct employees appearing in verification docs (for the log filter dropdown)."""
    pipeline = []
    if scope_query:
        pipeline.append({'$match': scope_query})
    pipeline += [
        {'$group': {'_id': '$employee_id', 'name': {'$first': '$employee_name'}}},
        {'$sort': {'name': 1}},
    ]
    return [{'id': doc['_id'], 'name': doc['name']}
            for doc in db.timesheetVerificationMaster.aggregate(pipeline)]


def get_week_entries(user_id, week_start):
    """Timesheet entries for Mon-Sat of the given week, grouped by 'YYYY-MM-DD'."""
    start = _normalize_date(week_start)
    end = start + timedelta(days=5)
    entries = list(db.timesheetMaster.find(
        {'user_id': str(user_id), 'date': {'$gte': start, '$lte': end}},
        {'_id': 0},
    ).sort('created_at', -1))
    grouped = {}
    for entry in entries:
        grouped.setdefault(entry['date'].strftime('%Y-%m-%d'), []).append(entry)
    return grouped


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
