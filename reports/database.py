import ssl
import pymongo
import datetime
from bson.objectid import ObjectId

__MONGO_CONNECTION_URI__ = 'mongodb://localhost/'

# __MONGO_CONNECTION_URI__ = 'mongodb+srv://Dhruvang:Diwan@cluster0.xp0yp.mongodb.net/test?retryWrites=true&w=majority&ssl=true'

client = pymongo.MongoClient(__MONGO_CONNECTION_URI__, 27017)
# client = pymongo.MongoClient(__MONGO_CONNECTION_URI__, ssl_cert_reqs=ssl.CERT_NONE)
db = client.HMD


def get_group_name_from_id(g_id):
    group_code = list(db.groupCode.find({}, {'_id': 0}))

    try:
        group_name = group_code[0][g_id]
        return group_name
    except:
        return 'ESD-DHD'


def get_ay_list():
    today_date = datetime.datetime.now()
    current_year = today_date.year
    start_year = 2010
    ay_list = []
    while start_year != current_year + 2:
        temp = str(start_year) + '-' + str(start_year + 1)
        start_year += 1
        ay_list.append(temp)

    return ay_list


def get_all_clients_details():
    return list(db.clientMaster.find({}, {'_id': 0, 'Client_no': 0, 'Contact_details.r_id': 0}))


def get_party_list():
    return list(db.partyMaster.aggregate([{'$group': {'_id': '$Group_name', 'party': {'$addToSet': '$Party_name'}}},
                                          {'$project': {'group': '$_id', '_id': 0, 'party': 1}}]))


def get_roi_result(client_name, group_name_list, ay, read, party):
    if read == 'All':
        result = list(db.returnMaster.find({'Name': {'$in': client_name}, 'AY': {'$in': ay}}))
    elif read == 'Unread':
        result = list(db.returnMaster.find({'Read': {'$ne': 'Read'}, 'Name': {'$in': client_name}, 'AY': {'$in': ay}}))
    else:
        result = list(db.returnMaster.find({'Read': 'Read', 'Name': {'$in': client_name}, 'AY': {'$in': ay}}))
    for data in result:
        data['Group_name'] = get_group_name_from_client_name(data['Name'])
        data['Client_code'] = get_client_code_from_name(data['Name'])
        data['Party_name'] = get_party_name_from_name(data['Name'])
        data['Task'] = "IT Return - " + data['Type']
        data['Start_date'] = data['Acceptance_date']
        data['Year'] = "AY - " + data['AY']
        try:
            data['End_date'] = data['Filing_date']
        except:
            data['End_date'] = '-'
        data['Type'] = 'ROI'

    return result


def get_cert_result(client_name, group_name_list, period, read, party):
    if read == 'All':
        result = list(db.certificateMaster.find({'Name':  {'$in': client_name}}))
    elif read == 'Unread':
        result = list(db.certificateMaster.find({'Read': {'$ne': 'Read'}, 'Name': {'$in': client_name}}))
    else:
        result = list(db.certificateMaster.find({'Read': 'Read', 'Name': {'$in': client_name}}))
    new_result = []

    for data in result:
        date_of_accept_str = data['Acceptance_date']
        try:
            date_of_cert = datetime.datetime.strptime(data['Date_of_certificate'], '%Y-%m-%d')
        except:
            date_of_cert = '-'
        try:
            date_of_accept = datetime.datetime.strptime(data['Acceptance_date'], '%Y-%m-%d')
        except:
            date_of_accept = datetime.datetime.now()

        if date_of_accept > datetime.datetime.strptime(period['Start_date'], '%Y-%m-%d'):
            new_result.append(data)

    for data in new_result:
        data['Group_name'] = get_group_name_from_client_name(data['Name'])
        data['Client_code'] = get_client_code_from_name(data['Name'])
        data['Party_name'] = get_party_name_from_name(data['Name'])
        data['Task'] = "Certificate - " + data['Description']
        data['Year'] = ''
        data['Start_date'] = date_of_accept_str
        data['End_date'] = date_of_cert
        data['Type'] = 'Certificate'
    return new_result


def get_other_result(client_name, group_name_list, period, read, party):
    if read == 'All':
        result = list(db.otherFormsMaster.find({'Name': {'$in': client_name}}))
    elif read == 'Unread':
        result = list(db.otherFormsMaster.find({'Read': {'$ne': 'Read'}, 'Name': {'$in': client_name}}))
    else:
        result = list(db.otherFormsMaster.find({'Read': 'Read', 'Name': {'$in': client_name}}))
    new_result = []

    for data in result:
        date_of_accept_str = data['Acceptance_date']
        try:
            date_of_cert = datetime.datetime.strptime(data['Date_of_document'], '%Y-%m-%d')
        except:
            date_of_cert = '-'
        try:
            date_of_accept = datetime.datetime.strptime(data['Acceptance_date'], '%Y-%m-%d')
        except:
            date_of_accept = datetime.datetime.now()
        if date_of_accept > datetime.datetime.strptime(period['Start_date'], '%Y-%m-%d'):
            new_result.append(data)

    for data in new_result:
        data['Group_name'] = get_group_name_from_client_name(data['Name'])
        data['Client_code'] = get_client_code_from_name(data['Name'])
        data['Party_name'] = get_party_name_from_name(data['Name'])
        data['Task'] = "Other - " + data['Description']
        data['Year'] = ''
        data['Start_date'] = date_of_accept_str
        data['End_date'] = date_of_cert
        data['Type'] = 'Other'
    return new_result


def get_client_code_from_name(name):
    clientMaster_result = list(db.clientMaster.find({'Name': name}, {'Client_code': 1}))
    if clientMaster_result:
        return clientMaster_result[0]['Client_code']
    else:
        return ''


def get_group_name_from_client_name(c_name):
    result = list(db.clientMaster.find({'Name': c_name}, {'Group_name': 1}))
    if result:
        return result[0]['Group_name']
    return 'NA'


def get_party_name_from_name(name):
    clientMaster_result = list(db.clientMaster.find({'Name': name}, {'Party_name': 1}))
    if clientMaster_result:
        return clientMaster_result[0]['Party_name']
    else:
        return ''


def get_r_type(r_type):
    if r_type == 'ROI':
        return 'ROI'
    elif 'Certificate' in r_type:
        return 'Certificate'
    elif 'Other' in r_type:
        return 'Other'
    else:
        return None


def get_record_from_db(r_id, type_name):
    result = []
    if type_name == 'ROI':
        result = list(db.returnMaster.find({'_id': ObjectId(r_id)}))
    elif type_name == 'Certificate':
        result = list(db.certificateMaster.find({'_id': ObjectId(r_id)}))
    elif type_name == 'Other':
        result = list(db.otherFormsMaster.find({'_id': ObjectId(r_id)}))

    if result:
        return result[0]
    else:
        return None


def submit_read_info(r_id, type_name, read, reader, remark):
    if type_name == 'ROI':
        x = db.returnMaster.update_one({'_id': ObjectId(r_id)}, {'$set': {'Read': read, 'Reader': reader,
                                                                          'Report_remarks': remark}})
        return x
    elif type_name == 'Certificate':
        x = db.certificateMaster.update_one({'_id': ObjectId(r_id)}, {'$set': {'Read': read, 'Reader': reader,
                                                                               'Report_remarks': remark}})
        return x
    elif type_name == 'Other':
        x = db.otherFormsMaster.update_one({'_id': ObjectId(r_id)}, {'$set': {'Read': read, 'Reader': reader,
                                                                              'Report_remarks': remark}})
        return x
    else:
        return []


def get_return_type_name_from_id(r_id):
    if r_id == '1':
        return 'Original'
    elif r_id == '2':
        return 'Revised'
    elif r_id == '3':
        return '142(1)'
    elif r_id == '4':
        return '148'
    elif r_id == '5':
        return '139(9)'
    elif r_id == '6':
        return '153A'
    elif r_id == '7':
        return '153C r.w 153A'
    elif r_id == '8':
        return '92CD'
    elif r_id == '9':
        return '119(2)(b)'
    else:
        return 'Original'


def get_return_type_id_from_name(name):
    if name == 'Original':
        return '1'
    elif name == 'Revised':
        return '2'
    elif name == '142(1)':
        return '3'
    elif name == '148':
        return '4'
    elif name == '139(9)':
        return '5'
    elif name == '153A':
        return '6'
    elif name == '153C r.w 153A':
        return '7'
    elif name == '92CD':
        return '8'
    elif name == '119(2)(b)':
        return '9'
    else:
        return '1'

