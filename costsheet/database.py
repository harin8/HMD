import bcrypt
import pymongo
import datetime
from bson.objectid import ObjectId

__MONGO_CONNECTION_URI__ = 'mongodb://localhost/'

client = pymongo.MongoClient(__MONGO_CONNECTION_URI__, 27017)
db = client.HMD


def get_record_from_db(r_id, type_name):
    result = []
    if type_name == 'ROI':
        result = list(db.returnMaster.find({'_id': ObjectId(r_id)}, {'_id': 0, 'Name': 1, 'Type': 1, 'AY': 1, 'Remarks': 1}))
    elif type_name == 'Certificate':
        result = list(db.certificateMaster.find({'_id': ObjectId(r_id)}, {'_id': 0, 'Name': 1, 'Description': 1, 'Remarks': 1}))
    elif type_name == 'Other':
        result = list(db.otherFormsMaster.find({'_id': ObjectId(r_id)}, {'_id': 0, 'Name': 1, 'Description': 1, 'Remarks': 1}))
    elif type_name == 'TDS':
        result = list(db.tdsMaster.find({'_id': ObjectId(r_id)}, {'_id':0, 'Name':1, 'Type': 1, 'AY': 1, 'Form': 1, 'Quarter': 1, 'Remarks': 1}))
    elif type_name == 'Proceedings':
        result = list(db.proceedingsMaster.find({'_id': ObjectId(r_id)}, {'_id': 0, 'Name': 1, 'AY': 1, 'Description': 1, 'Section': 1, 'Case_reference_no': 1, 'Closure_particulars': 1, 'Remarks': 1}))

    if result:
        return result[0]
    else:
        return None
    

def get_client_details_from_name(name):
    result = list(db.clientMaster.find({'Name': name}, {'_id': 0,  'Party_name': 1, 'Group_name': 1, 'It_no': 1, 'Audit_no': 1}))
    if result:
        return result[0]
    else:
        return None