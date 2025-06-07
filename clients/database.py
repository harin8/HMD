import bcrypt
import pymongo
from bson import ObjectId
import datetime
from datetime import datetime

__MONGO_CONNECTION_URI__ = 'mongodb://localhost/'

client = pymongo.MongoClient(__MONGO_CONNECTION_URI__, 27017)
db = client.HMD

if __name__ == "__main__":
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


def insert_group_code_to_db_new(g_c, g_n):
    db.groupCode.update_one({}, {"$set": {g_c: g_n}}, True)


def insert_new_group_to_db(g_n, g_r, h_n):
    today_date = datetime.now()
    if "OS-" in g_n:
        db.clientCodeRule.insert_one({"Group": g_n, "Start": 9000, "End": 9200, "Heads": h_n,
                                      "Date_of_creation": today_date})
    else:
        db.clientCodeRule.insert_one({"Group": g_n, "Start": int(g_r), "End": int(g_r) + 200, "Heads": h_n,
                                      "Date_of_creation": today_date})


def get_all_group_code_name():
    result = list(db.groupCode.find({}, {"_id": 0}))
    return result[0]


def get_group_name_from_id(g_id):
    group_code = list(db.groupCode.find({}, {'_id': 0}))

    try:
        group_name = group_code[0][g_id]
        return group_name
    except:
        return 'ESD-DHD'


def check_it_code_present(it_no):
    result = list(db.clientMaster.find({'It_no': it_no}))
    if result:
        return True
    return False


def check_client_name_present(client_name):
    result = list(db.clientMaster.find({'Name': client_name}))
    if result:
        return True
    else:
        return False


def get_group_code_from_group_name(g_name):
    group_list = list(db.groupCode.find({}, {'_id': 0}))
    for data in group_list:
        for x, y in data.items():
            if y == g_name:
                return x
    return 0


def get_it_audit_size(it_id):
    if it_id == '0':
        return 'NA'
    elif it_id == '1':
        return 'Big'
    elif it_id == '2':
        return 'Medium'
    elif it_id == '3':
        return 'Small'
    else:
        return 'NA'


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
        return 'IND./HUF/OTHERS'
    else:
        return 'COMPANY'


def get_client_master_list(id_field=False):
    if id_field:
        result = list(db.clientMaster.find({}, {'_id': 1, 'Contact_details.r_id': 0}))
    else:
        result = list(db.clientMaster.find({}, {'_id': 0, 'Contact_details.r_id': 0}))
    return result


def get_closed_client_master_list(id_field=False):
    if id_field:
        result = list(db.closedClientMaster.find({}, {'_id': 1, 'Contact_details.r_id': 0}))
    else:
        result = list(db.closedClientMaster.find({}, {'_id': 0, 'Contact_details.r_id': 0}))
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


def get_all_gst_value():
    result = db.clientMaster.distinct('GST_no')
    return result


def get_all_distinct_value(field_name):
    result = db.clientMaster.distinct(field_name)
    return result


def add_client_details(data_dict):
    return db.clientMaster.insert_one(data_dict)


def update_client_details_edit(client_id, data_dict):
    return db.clientMaster.update_one({'_id': ObjectId(client_id)}, {'$set': data_dict})


def add_party_details(data_dict):
    # check if exists
    result = list(db.partyMaster.find({"Party_name": data_dict['Party_name']}, {'_id': 1}))
    if result:
        return []
    else:
        return db.partyMaster.insert_one(data_dict)


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


def get_gst_no_range():
    return 1, 9999


def get_party_list_from_group_name(group_name):
    return db.partyMaster.distinct('Party_name', {'Group_name': group_name})


def get_client_detail_from_id(id):
    result = list(db.clientMaster.find({'_id': ObjectId(id)}))
    if result:
        return result[0]
    return None


def get_party_master_list(id_field):
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


def transfer_party(r_id, temp):
    # Code to add party in closed party list in db
    result = db.partyMaster.update_one({'_id': ObjectId(r_id)}, temp)


def close_party(r_id, temp):
    # Code to add party in closed party list in db
    db.closedPartyMaster.insert_one(temp)
    db.partyMaster.remove({'_id': ObjectId(r_id)})


def get_total_client_from_party_name(party_name):
    result = db.clientMaster.count_documents({'Party_name': party_name})
    return result


def get_all_available_group_no():
    result = list(db.clientCodeRule.distinct("Start", {'Group': {'$exists': True}}))
    all_possible_list = [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000]
    available_list = sorted(list(set(all_possible_list) - set(result)))
    available_list.append(9000)
    return available_list


def get_all_available_group_code():
    result = list(db.groupCode.find({}, {'_id': 0}))
    return result


def get_all_group_list():
    result = list(db.clientCodeRule.find({"Group": {"$exists": True}}, {"_id": 0}))
    return result


def get_empty_group_list():
    party_result = list(db.partyMaster.distinct("Group_name"))
    group_result = list(db.clientCodeRule.distinct("Group", {"Group": {"$exists": True}}))

    can_close_group_list = list(set(group_result) - set(party_result))
    return can_close_group_list


def close_group_database(group_name, close_reason):
    existing_group_code = get_all_group_code_name()
    new_group_code_dict = {}
    group_list = []
    for k, v in existing_group_code.items():
        group_list.append(v)
    if group_name in group_list:
        group_list.remove(group_name)
        for x in range(len(group_list)):
            new_group_code_dict[str(x)] = group_list[x]
        db.groupCode.remove({})
        db.groupCode.insert_one(new_group_code_dict)

        db.clientCodeRule.delete_many({"Group": group_name})
        today_date = datetime.now()
        close_group_db = db["closedGroupMaster"]
        result = db.closedGroupMaster.insert_one({"Group": group_name, "Reason": close_reason,
                                              "Date_of_closure": today_date})
        return result

    else:
        return None


def get_closed_group_list():
    result = list(db.closedGroupMaster.find({}))
    return result


def get_all_distinct_group_names():
    result = list(db.clientCodeRule.distinct("Group"))
    return result


def get_all_distinct_clients_from_party_name(party):
    result = list(db.clientMaster.aggregate([
        {
            '$match': {
                'Party_name': party
            }
        }, {
            '$project': {
                '_id': 1,
                'Name': 1,
                'It_no': 1,
                'It_size': 1,
                'Audit_no': 1,
                'Audit_size': 1,
                'Client_type': 1,
                'Group_name': 1
            }
        }
    ]))
    return result


def update_party_name_in_party_master(group_name, new_party_name):
    # Assuming you have a connection to the database and a reference to the partyMaster collection
    collection = db.partyMaster

    # Update the party name for the specified group name in the partyMaster collection
    collection.update_many(
        {'Party_name': new_party_name},
        {'$set': {'Group_name': group_name}}
    )


def update_client_details(updated_data_list):
    for each_client in updated_data_list:
        db.tdsMaster.update_many({"Client_code": each_client['OldITNo']},
                                 {"$set": {"Client_code": each_client['It_no']}})
        db.returnMaster.update_many({"It_no": each_client['OldITNo']}, {"$set": {"It_no": each_client['It_no']}})
        db.clientMaster.update_one({"_id": ObjectId(each_client['Client_id'])}, {"$set": each_client})


def close_client(client_detail):
    # return master IT_code, Name
    # tds master - Client_code, Name
    # proceeding master - Name
    # certificate master - Name
    # other form master - Name

    # check if any returns are pending

    unread_returns = list(
        db.returnMaster.aggregate([{"$match": {"Name": client_detail['clientName'], "Read": {"$exists": False}}}]))
    unread_tds = list(
        db.tdsMaster.aggregate([{"$match": {"Name": client_detail['clientName'], "Read": {"$exists": False}}}]))
    unread_proceedings = list(
        db.proceedingsMaster.aggregate([{"$match": {"Name": client_detail['clientName'], "Read": {"$exists": False}}}]))
    unread_certificates = list(
        db.certificateMaster.aggregate([{"$match": {"Name": client_detail['clientName'], "Read": {"$exists": False}}}]))
    unread_other_forms = list(
        db.otherFormsMaster.aggregate([{"$match": {"Name": client_detail['clientName'], "Read": {"$exists": False}}}]))
    if unread_returns or unread_tds or unread_proceedings or unread_certificates or unread_other_forms:
        return 0, "Selected client may have incompleted task(s)."
    else:
        # update client_code, audit_code, it_code, party_name
        closed_it_code = "C-" + client_detail['itCode']
        closed_audit_code = "C-" + client_detail['auditCode']
        closed_party_name = "C-" + client_detail['partyName']
        today_date = datetime.now()
        selected_client_details = list(db.clientMaster.find({'Name': client_detail['clientName']}))
        if not selected_client_details:
            return 0, "No such client exists with this name"
        selected_client_details[0]['Client_code'] = closed_it_code
        selected_client_details[0]['It_no'] = closed_it_code
        selected_client_details[0]['Audit_no'] = closed_audit_code
        selected_client_details[0]['Party_name'] = closed_party_name
        selected_client_details[0]['Closure_date'] = today_date
        selected_client_details[0]['Closure_remarks'] = client_detail['closureRemark'].upper()
        try:
            db.closedClientMaster.insert_one(selected_client_details[0])
            db.clientMaster.delete_one({'Name': client_detail['clientName']})
            db.returnMaster.update_many({'Name': client_detail['clientName']}, {'$set': {'It_no': closed_it_code,
                                                                                         'Client_closed': True}})
            db.tdsMaster.update_many({'Name': client_detail['clientName']}, {'$set': {'Client_code': closed_it_code,
                                                                                      'Client_closed': True}})
            db.proceedingsMaster.update_many({'Name': client_detail['clientName']}, {'$set': {'Client_closed': True}})
            db.certificateMaster.update_many({'Name': client_detail['clientName']}, {'$set': {'Client_closed': True}})
            db.otherFormsMaster.update_many({'Name': client_detail['clientName']}, {'$set': {'Client_closed': True}})
            return 1, "Client Closed"
        except Exception as ex:
            return 0, "Some error happened when updating database"


def verify_password(operation_name, entered_password):
    stored_salt_result = db.credentials.find_one({'Operation': "Salt"}, {"Salt": 1})
    if stored_salt_result:
        stored_salt = stored_salt_result['Salt']
        stored_hashed_password_result = db.credentials.find_one({'Operation': operation_name}, {"Password": 1})
        if stored_hashed_password_result:
            stored_password_hashed = stored_hashed_password_result['Password']
            entered_password_hashed = bcrypt.hashpw(entered_password.encode('utf-8'), stored_salt)
            if entered_password_hashed == stored_password_hashed:
                return True
            else:
                return False
        else:
            return False
    else:
        return False
