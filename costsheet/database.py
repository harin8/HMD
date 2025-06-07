from pymongo import MongoClient
from django.conf import settings

def get_client_details_from_name(client_name):
    client = MongoClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_NAME]
    collection = db['clients']
    
    client_details = collection.find_one({'Name': client_name})
    if client_details:
        return {
            'Party_name': client_details.get('Party_name', ''),
            'Group_name': client_details.get('Group_name', ''),
            'It_no': client_details.get('It_no', ''),
            'Audit_no': client_details.get('Audit_no', '')
        }
    return {
        'Party_name': '',
        'Group_name': '',
        'It_no': '',
        'Audit_no': ''
    }

def get_record_from_db(record_id, type_name):
    client = MongoClient(settings.MONGODB_URI)
    db = client[settings.MONGODB_NAME]
    collection = db[type_name.lower()]
    
    return collection.find_one({'_id': record_id}) 