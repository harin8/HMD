import pymongo
import datetime
from datetime import datetime

__MONGO_CONNECTION_URI__ = 'mongodb://localhost/'

client = pymongo.MongoClient(__MONGO_CONNECTION_URI__, 27017)
db = client.HMD


def date_to_IST_format(date):
    try:
        return date.strftime("%d-%m-%Y")
    except AttributeError:
        # convert to date object
        try:
            date_type = datetime.strptime(date, '%Y-%m-%d')
        except:
            return '-'
        return date_type.strftime("%d-%m-%Y")


def ymd_str_to_IST_format(date_str):
    try:
        date_type = datetime.strptime(date_str, '%Y-%m-%d')
        return date_type.strftime("%d-%m-%Y")
    except Exception:
        return ''


def get_ay_list():
    today_date = datetime.now()
    current_year = today_date.year
    start_year = 2010
    ay_list = []
    while start_year != current_year + 2:
        temp = str(start_year) + '-' + str(start_year + 1)
        start_year += 1
        ay_list.append(temp)

    return ay_list[::-1]


def get_tds_form_list():
    result = list(db.tdsForm.find({}, {'_id': 0}))
    if result:
        return result[0]
    return {}


def get_tds_type_list():
    result = list(db.tdsType.find({}, {'_id': 0}))
    if result:
        return result[0]
    return {}


def get_tds_quarter_list():
    result = list(db.quarterList.find({}, {'_id': 0}))
    if result:
        return result[0]
    return {}


def get_tds_form_name_from_id(form_id):
    result = get_tds_form_list()
    if result:
        for key, value in result.items():
            if key == form_id:
                return value
        return ''
    return ''


def get_tds_form_id_from_name(form_name):
    result = get_tds_form_list()
    if result:
        for key, value in result.items():
            if value == form_name:
                return key
        return ''
    return ''


def get_tds_type_name_from_id(type_id):
    result = get_tds_type_list()
    if result:
        for key, value in result.items():
            if key == type_id:
                return value
        return ''
    return ''


def get_tds_type_id_from_name(type_name):
    result = get_tds_type_list()
    if result:
        for key, value in result.items():
            if value == type_name:
                return key
        return ''
    return ''


def get_tds_quarter_name_from_id(quarter_id):
    result = get_tds_quarter_list()
    if result:
        for key, value in result.items():
            if key == quarter_id:
                return value
        return ''
    return ''


def get_tds_quarter_id_from_name(quarter_name):
    result = get_tds_quarter_list()
    if result:
        for key, value in result.items():
            if value == quarter_name:
                return key
        return ''
    return ''


def get_client_name_from_client_code(client_no):
    name = list(db.clientMaster.find({'Client_code': client_no}, {'Name': 1}))
    if name:
        return name[0]['Name']
    return ''


def get_all_tds_list(tds_ay, tds_type, tds_form, tds_quarter):
    result = list(db.tdsMaster.find({'AY': tds_ay, 'Type': tds_type, 'Form': tds_form, 'Quarter': tds_quarter,
                                     'Client_closed': {'$exists': False}},
                                    {'_id': 0}))
    master_client = db.clientMaster.distinct('Client_code', {'TDS': "True"})
    return_client = db.tdsMaster.distinct('Client_code', {'AY': tds_ay, 'Type': tds_type, 'Form': tds_form,
                                                          'Quarter': tds_quarter})
    diff_client = list(set(master_client) - set(return_client))
    for cl in diff_client:
        result_client = list(db.clientMaster.find({'Client_code': cl}, {'_id': 0, 'Contact_details.r_id': 0}))
        for x in result_client:
            x['Type'] = tds_type
            x['AY'] = tds_ay
            x['Form'] = tds_form
            x['Quarter'] = tds_quarter
            x['Status'] = 'Not initiated'
        result.extend(result_client)

    return result


def get_tds_details(client_no, ay, quarter, form, type):
    result = list(
        db.tdsMaster.find({'Client_code': client_no, 'AY': ay, 'Quarter': quarter, 'Form': form, 'Type': type},
                          {'_id': 0}))
    if result:
        return result[0]
    else:
        result = list(db.clientMaster.find({'Client_code': client_no}, {'Name': 1, 'Client_code': 1}))
        if result:
            return result[0]
        else:
            return {'Name': ''}


def add_tds_record(data_dict):
    # check if exists in db
    exists_result = list(db.tdsMaster.find({'Client_code': data_dict['Client_code'], 'Type': data_dict['Type'],
                                            'AY': data_dict['AY'], 'Form': data_dict['Form'],
                                            'Quarter': data_dict['Quarter']},
                                           {'_id': 1}))

    if exists_result:
        record_id = exists_result[0]['_id']
        x = db.tdsMaster.replace_one({'_id': record_id}, data_dict)
    else:
        x = db.tdsMaster.insert_one(data_dict)
    return x


def get_client_code_from_name(name):
    clientMaster_result = list(db.clientMaster.find({'Name': name}, {'Client_code': 1}))
    if clientMaster_result:
        return clientMaster_result[0]['Client_code']
    else:
        return ''


def get_group_name_from_client_code(c_code):
    result = list(db.clientMaster.find({'Client_code': c_code}, {'Group_name': 1}))
    if result:
        return result[0]['Group_name']
    return 'NA'


def get_existing_completed_tds_list():
    result = list(db.tdsMaster.find({'$or': [{'Status': 'Completed'}, {'Status': 'Initiated'}],
                                     'Client_closed': {'$exists': False}}, {'_id': 0}))
    return result


def get_tds_filing_mode_name_from_id(r_id):
    if r_id == '1':
        return 'SELF'
    elif r_id == '2':
        return 'EXTERNAL AGENT'
    elif r_id == '-1':
        return ''
    else:
        return ''


def add_further_tds_record(data_dict):
    # check if exists in db
    exists_result = list(db.tdsMaster.find({'Client_code': data_dict['Client_code'], 'Type': data_dict['Type'],
                                            'AY': data_dict['AY'], 'Quarter': data_dict['Quarter'],
                                            'Form': data_dict['Form'], 'Status': 'Initiated'}, {'_id': 1}))
    if exists_result:
        record_id = exists_result[0]['_id']
        if data_dict['Submitted_fur']:
            x = db.tdsMaster.update_one({'_id': record_id}, {'$set': {'Status': 'Completed',
                                                                      'Handled_by': data_dict['Handled_by'],
                                                                      'Checked_by': data_dict['Checked_by'],
                                                                      'Filing_date': data_dict['Filing_date'],
                                                                      'Filing_mode': data_dict['Filing_mode'],
                                                                      'Token_no': data_dict['Token_no'],
                                                                      'Remarks': data_dict['Remarks'],
                                                                      'Filed_by': data_dict['Filed_by'],
                                                                      'Submitted_fur': data_dict['Submitted_fur'],
                                                                      'Submitted_ini': True}})
        else:
            x = db.tdsMaster.update_one({'_id': record_id}, {'$set': {'Status': 'Initiated',
                                                                      'Handled_by': data_dict['Handled_by'],
                                                                      'Checked_by': data_dict['Checked_by'],
                                                                      'Filing_date': data_dict['Filing_date'],
                                                                      'Filing_mode': data_dict['Filing_mode'],
                                                                      'Token_no': data_dict['Token_no'],
                                                                      'Remarks': data_dict['Remarks'],
                                                                      'Filed_by': data_dict['Filed_by'],
                                                                      'Submitted_fur': data_dict['Submitted_fur']}})
    else:
        x = None
        print('not updated')
    return x


def delete_tds_return(client_code, ay, quarter_id, form_id, type_id):
    result = db.tdsMaster.delete_one({'Client_code': client_code, 'AY': ay, 'Quarter': quarter_id, 'Form': form_id,
                                      'Type': type_id})
    if result.deleted_count > 0:
        return True
    else:
        return False
