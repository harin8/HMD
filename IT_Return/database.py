import ssl
import pymongo
import datetime
from datetime import timedelta

# __MONGO_CONNECTION_URI__ = 'mongodb://localhost/'
__MONGO_CONNECTION_URI__ = 'mongodb+srv://Dhruvang:Diwan@cluster0.xp0yp.mongodb.net/test?retryWrites=true&w=majority&ssl=true'


# client = pymongo.MongoClient(__MONGO_CONNECTION_URI__, 27017)
client = pymongo.MongoClient(__MONGO_CONNECTION_URI__, ssl_cert_reqs=ssl.CERT_NONE)
db = client.HMD


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


def get_return_proof_name_from_id(r_id):
    if r_id == '1':
        return 'DSC'
    elif r_id == '2':
        return 'Aadhar'
    elif r_id == '3':
        return 'CPC'
    elif r_id == '4':
        return 'Verify Later'
    elif r_id == '5':
        return 'EVC'
    else:
        return 'DSC'


def get_all_return_list(r_ay, r_type):
    result = list(db.returnMaster.find({'AY': r_ay, 'Type': r_type}, {'_id': 0}))
    master_client = db.clientMaster.distinct('It_no')
    return_client = db.returnMaster.distinct('It_no', {'AY': r_ay, 'Type': r_type})
    diff_client = list(set(master_client) - set(return_client))
    for cl in diff_client:
        result_client = list(db.clientMaster.find({'It_no': cl}, {'_id': 0, 'Name': 1, 'It_no': 1, 'Audit_no': 1}))
        for x in result_client:
            x['Type'] = r_type
            x['AY'] = r_ay
            x['Status'] = 'Not initiated'
        result.extend(result_client)
    return result


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


def add_return_record(data_dict):
    # check if exists in db
    exists_result = list(db.returnMaster.find({'It_no': data_dict['It_no'], 'Type': data_dict['Type'],
                                               'AY': data_dict['AY']}, {'_id': 1}))

    if exists_result:
        record_id = exists_result[0]['_id']
        x = db.returnMaster.replace_one({'_id': record_id}, data_dict)
    else:
        x = db.returnMaster.insert_one(data_dict)
    return x


def get_return_details(it_no, ay, r_type_name):
    result = list(db.returnMaster.find({'It_no': it_no, 'AY': ay, 'Type': r_type_name}, {'_id': 0}))
    if result:
        return result[0]
    else:
        result = list(db.clientMaster.find({'It_no': it_no}, {'Name': 1, 'It_no': 1}))
        if result:
            return result[0]
        else:
            return {'Name': ''}


def get_client_code_from_result(result):
    if result:
        result['Client_code'] = get_client_code_from_name(result['Name'])
    return result


def get_client_code_from_name(name):
    clientMaster_result = list(db.clientMaster.find({'Name': name}, {'Client_code': 1}))
    if clientMaster_result:
        return clientMaster_result[0]['Client_code']
    else:
        return ''


def add_further_return_record(data_dict):
    # check if exists in db
    exists_result = list(db.returnMaster.find({'Name': data_dict['Name'], 'Type': data_dict['Type'],
                                               'AY': data_dict['AY'], 'Status': 'Initiated'}, {'_id': 1}))

    if exists_result:
        record_id = exists_result[0]['_id']
        if data_dict['Submitted_fur']:
            x = db.returnMaster.update_one({'_id': record_id}, {'$set': {'Status': 'Completed',
                                                                         'Handled_by': data_dict['Handled_by'],
                                                                         'Checked_by': data_dict['Checked_by'],
                                                                         'Filing_date': data_dict['Filing_date'],
                                                                         'Verification': data_dict['Verification'],
                                                                         'Ack_no': data_dict['Ack_no'],
                                                                         'Remarks': data_dict['Remarks'],
                                                                         'Filed_by': data_dict['Filed_by'],
                                                                         'Submitted_fur': data_dict['Submitted_fur'],
                                                                         'Submitted_ini': True}})
        else:
            x = db.returnMaster.update_one({'_id': record_id}, {'$set': {'Status': 'Initiated',
                                                                         'Handled_by': data_dict['Handled_by'],
                                                                         'Checked_by': data_dict['Checked_by'],
                                                                         'Filing_date': data_dict['Filing_date'],
                                                                         'Verification': data_dict['Verification'],
                                                                         'Ack_no': data_dict['Ack_no'],
                                                                         'Remarks': data_dict['Remarks'],
                                                                         'Filed_by': data_dict['Filed_by'],
                                                                         'Submitted_fur': data_dict['Submitted_fur']}})
    else:
        x = None
        print('not updated')
    return x


def get_existing_completed_return_list():
    result = list(db.returnMaster.find({'$or': [{'Status': 'Completed'}, {'Status': 'Initiated'}]}, {'_id': 0}))
    return result


def get_cpc_all_return_list():
    result = list(db.returnMaster.find({'$and': [{'Submitted_fur': True},
                                                 {'$or': [{'Verification': 'Verify Later'}, {'Verification': 'Aadhar'},
                                                          {'Verification': 'EVC'}]}]}, {'_id': 0}))
    for x in result:
        clientMaster_result = list(db.clientMaster.find({'Name': x['Name']}, {'It_no': 1}))
        if clientMaster_result:
            x['Client_code'] = clientMaster_result[0]['It_no']
        else:
            x['Client_code'] = ''
    return result


def get_client_master_list():
    result = list(db.clientMaster.find({}, {'_id': 0}))
    return result


def calculate_due_date_cpc(result):
    if result:
        try:
            filing_date = result['Filing_date']
        except:
            return result
        result['Due_date_cpc'] = datetime.datetime.strftime(datetime.datetime.strptime(filing_date, '%Y-%m-%d') +
                                                            timedelta(days=120), "%Y-%m-%d")

    return result


def add_cpc_return_record(data_dict):
    # check if exists in db
    exists_result = list(db.returnMaster.find({'Name': data_dict['Name'], 'Type': data_dict['Type'],
                                               'AY': data_dict['AY'], 'Status': 'Completed'}, {'_id': 1}))
    if exists_result:
        record_id = exists_result[0]['_id']
        x = db.returnMaster.update_one({'_id': record_id}, {'$set': {'Remarks_cpc': data_dict['Remarks_cpc'],
                                                                     'Completed_by': data_dict['Completed_by'],
                                                                     'Completed_on': data_dict['Completed_on'],
                                                                     'Due_date': data_dict['Due_date'],
                                                                     'Verification': data_dict['Verification'],
                                                                     'Submitted_cpc': True}})
    else:
        x = None
        print('not updated')
    return x
