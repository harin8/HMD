import pymongo
from bson import ObjectId

__MONGO_CONNECTION_URI__ = 'mongodb://localhost/'

client = pymongo.MongoClient(__MONGO_CONNECTION_URI__, 27017)
db = client.HMD


def insert_group_code_to_db():
    data = {
        "0": "ESD-DHD",
        "1": "ESD-NRJ",
        "2": "OS-ESD",
        "3": "VHD",
        "4": "PRB",
        "5": "RIS",
        "6": "OS-VHD",
        "7": "OS-PRB",
        "8": "OS-RIS",
    }
    db.groupCode.insert_one(data)


def get_group_name_from_id(g_id):
    group_code = list(db.groupCode.find({}, {'_id': 0}))

    try:
        group_name = group_code[0][g_id]
        return group_name
    except:
        return 'ESD-DHD'


def get_group_code_from_group_name(g_name):
    group_list = list(db.groupCode.find({}, {'_id': 0}))
    for data in group_list:
        for x, y in data.items():
            print(y)
            if y == g_name:
                return x
    return 0


def get_it_audit_size(it_id):
    if it_id == '0':
        return 'N.A'
    elif it_id == '1':
        return 'Big'
    elif it_id == '2':
        return 'Medium'
    elif it_id == '3':
        return 'Small'
    else:
        return 'N.A'


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


def calculate_party_size(client_info_list):
    if client_info_list:
        for size in client_info_list:
            if size['It_size']:
                size['Big_it'] = size['It_size'].count('Big')
                size['Medium_it'] = size['It_size'].count('Medium')
                size['Small_it'] = size['It_size'].count('Small')
            else:
                size['Big_it'] = size['Medium_it'] = size['Small_it'] = 0
            if size['Audit_size']:
                size['Big_audit'] = size['Audit_size'].count('Big')
                size['Medium_audit'] = size['Audit_size'].count('Medium')
                size['Small_audit'] = size['Audit_size'].count('Small')
            else:
                size['Big_audit'] = size['Medium_audit'] = size['Small_audit'] = 0
            size['Total_it'] = size['Big_it'] + size['Medium_it'] + size['Small_it']
            size['Total_audit'] = size['Big_audit'] + size['Medium_audit'] + size['Small_audit']
            size['Grand_total'] = size['Total_it'] + size['Total_audit']

    return client_info_list


def get_client_it_size_list():
    party_list = list(db.partyMaster.find({}, {'_id': 0}))
    result = list(db.clientMaster.aggregate([{'$group': {'_id': {'Group': '$Group_name', 'Party': '$Party_name'},
                                                         'It_size': {'$push': '$It_size'},
                                                         'Audit_size': {'$push': '$Audit_size'}}},
                                             {'$project': {'Group': '$_id.Group', 'Party': '$_id.Party',
                                                           'It_size': 1, 'Audit_size': 1}}]))
    group_list = list(db.clientMaster.aggregate([{'$group': {'_id': {'Group': '$Group_name', 'Party': '$Party_name'}}},
                                                 {'$project': {'Group_name': '$_id.Group', 'Party_name': '$_id.Party',
                                                               '_id': 0}}]))

    if party_list:
        for data in party_list:
            if data in group_list:
                continue
            else:
                temp = {'Group': data['Group_name'], 'Party': data['Party_name'], 'It_size': [], 'Audit_size': []}
                result.append(temp)

        final_result = calculate_party_size(result)
        return final_result

    return []


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
        if 'OS-' in group_name:
            start_no = group_no_range[0]['Start'] + 1
            end_no = group_no_range[0]['End'] + + 0
        else:
            start_no = group_no_range[0]['Start'] + type_no_range[0]['Start']
            end_no = group_no_range[0]['Start'] + type_no_range[0]['End']

        return start_no, end_no
    return 0, 0


def get_audit_no_range(group_name, client_type):
    group_no_range = db.clientCodeRule.find({'Group': group_name}, {'_id': 0})
    type_no_range = db.clientCodeRule.find({'Name': client_type, 'Type': "AUDIT"}, {'_id': 0})
    if group_no_range and type_no_range:
        if 'OS-' in group_name:
            start_no = 0
            end_no = -1
        else:
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
