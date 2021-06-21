import ssl
import pymongo

# __MONGO_CONNECTION_URI__ = 'mongodb://localhost/'
__MONGO_CONNECTION_URI__ = 'mongodb+srv://Dhruvang:Diwan@cluster0.xp0yp.mongodb.net/test?retryWrites=true&w=majority&ssl=true'
from bson import ObjectId

# client = pymongo.MongoClient(__MONGO_CONNECTION_URI__, 27017)
client = pymongo.MongoClient(__MONGO_CONNECTION_URI__, ssl_cert_reqs=ssl.CERT_NONE)
db = client.HMD


def get_group_name_from_id(g_id):
    if g_id == '1':
        return 'ESD'
    elif g_id == '2':
        return 'RIS'
    elif g_id == '3':
        return 'VHD'
    elif g_id == '4':
        return 'PRB'
    elif g_id == '5':
        return 'OS-ESD'
    elif g_id == '6':
        return 'OS-RIS'
    elif g_id == '7':
        return 'OS-VHD'
    elif g_id == '8':
        return 'OS-PRB'
    else:
        return 'ESD'


def get_client_type_name_from_id(c_id):
    if c_id == '1':
        return 'COMPANY'
    elif c_id == '2':
        return 'TRUST/AOP'
    elif c_id == '3':
        return 'LLP'
    elif c_id == '4':
        return 'FIRM'
    elif c_id == '5':
        return 'IND/HUF/OTHERS'
    else:
        return 'COMPANY'


def get_client_master_list(id_field=False):
    if id_field:
        result = list(db.clientMaster.find({}, {'_id': 1}))
    else:
        result = list(db.clientMaster.find({}, {'_id': 0}))
    return result


def get_all_distinct_value(field_name):
    result = db.clientMaster.distinct(field_name)
    return result


def add_client_details(data_dict):
    return db.clientMaster.insert(data_dict)


def add_party_details(data_dict):
    # check if exists
    result = list(db.partyMaster.find(data_dict, {'_id': 1}))
    if result:
        print('Not Inserted')
        return []
    else:
        return db.partyMaster.insert(data_dict)


def get_it_no_range(group_name, client_type):
    group_no_range = db.clientCodeRule.find({'Group': group_name}, {'_id': 0})
    type_no_range = db.clientCodeRule.find({'Name': client_type, 'Type': "IT"}, {'_id': 0})
    if group_no_range and type_no_range:
        start_no = group_no_range[0]['Start'] + type_no_range[0]['Start']
        end_no = group_no_range[0]['Start'] + type_no_range[0]['End']

        return start_no, end_no
    return 0, 0


def get_audit_no_range(group_name, client_type):
    group_no_range = db.clientCodeRule.find({'Group': group_name}, {'_id': 0})
    type_no_range = db.clientCodeRule.find({'Name': client_type, 'Type': "AUDIT"}, {'_id': 0})
    if group_no_range and type_no_range:
        start_no = group_no_range[0]['Start'] + type_no_range[0]['Start']
        end_no = group_no_range[0]['Start'] + type_no_range[0]['End']

        return start_no, end_no

    return 0, 0


def get_party_list_from_group_name(group_name):
    return db.partyMaster.distinct('Party_name', {'Group_name': group_name})


def get_client_detail_from_id(id):
    result = list(db.clientMaster.find({'_id': ObjectId(id)}))
    if result:
        return result[0]
    return None


def get_party_master_list(id_field=False):
    if id_field:
        result = list(db.partyMaster.find({}))
    else:
        result = list(db.partyMaster.find({}, {'_id': 0}))
    return result


def get_party_detail_from_id(id):
    result = list(db.partyMaster.find({'_id': ObjectId(id)}))
    if result:
        return result[0]
    return None


def update_party_details(r_id, temp):
    result = db.partyMaster.update({'_id': ObjectId(r_id)}, temp)