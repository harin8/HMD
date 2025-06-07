import pymongo
from bson.objectid import ObjectId
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


def check_client_from_client_code(client_code):
    result = list(db.clientMaster.find({'Client_code': client_code}, {'_id': 1, 'Name': 1}))
    if result:
        return True, result[0]['Name']
    return False, ''


def initialise_regdescription_id_mapping():
    result = list(db.regularProceedingsDescription.find({}, {'_id': 0}))

    if result:
        return result[0]
    return {'1': 'REGULAR ASSESSMENT PROCEEDINGS', '2': 'REASSESSMENT PROCEEDINGS',
            '3': 'SEARCH ASSESSMENT PROCEEDINGS', '4': 'PENALTY PROCEEDINGS'}


def initialise_juddescription_id_mapping():
    result = list(db.judicialProceedingsDescription.find({}, {'_id': 0}))

    if result:
        return result[0]
    return {'1': 'ITA_FORM 35_APPEAL TO CIT(A)', '2': 'ITA_FORM 36_APPEAL TO ITAT', '3': 'ITA_FORM 36A_CO TO ITAT',
            '4': 'ITA_MA TO ITAT', '5': 'HC WRIT / APPEAL / OTHER MATTER', '6': 'SC WRIT / APPEAL / OTHER MATTER',
            '7': 'ITA_REVISION APPLICATION U/S. 264', '8': 'ITA_STAY APP. BEFORE PCCIT/CCIT/PCIT',
            '9': 'ITA_STAY APP. BEFORE CIT(A)', '10': 'ITA_STAY APP. BEFORE ITAT',
            '11': 'SET ASIDE TO COMMISSIONER(APPEALS)', '12': 'SET ASIDE TO APPELLATE TRIBUNAL',
            '13': 'EL_FORM 3_APPEAL TO CIT(A)', '14': 'EL_FORM 4_APPEAL TO ITAT',
            '15': 'BLACK MONEY_FORM 2_APPEAL TO CIT(A)', '16': 'BLACK MONEY_FORM 3_APPEAL TO ITAT',
            '17': 'BLACK MONEY_FORM 4_CO TO ITAT', '18': 'BENAMI_FORM 3_APPEAL TO PBPT-AT'}


def get_id_from_regularproc_description_name(description):
    temp_dict = initialise_regdescription_id_mapping()
    for key, value in temp_dict.items():
        if value == description:
            return True
    return False


def get_id_from_judarproc_description_name(description):
    temp_dict = initialise_juddescription_id_mapping()
    for key, value in temp_dict.items():
        if value == description:
            return True
    return False


def get_all_clients_details():
    return list(db.clientMaster.find({}, {'_id': 0, 'Client_no': 0, 'Contact_details.r_id': 0}))


def get_all_proceedings_list():
    result = list(db.proceedingsMaster.find({'$and': [{'Type': 3}, {'Client_closed': {'$exists': False}}]}))
    for data in result:
        try:
            data['Base_date'] = date_to_IST_format(data['Base_date'])
        except:
            data['Base_date'] = "-"
        try:
            data['Closure_date'] = date_to_IST_format(data['Closure_date'])
        except:
            data['Closure_date'] = "-"
        try:
            data['Event_actual_date'] = date_to_IST_format(data['Event_actual_date'])
        except:
            data['Event_actual_date'] = "-"
        try:
            data['Actual_closure_date'] = date_to_IST_format(data['Actual_closure_date'])
        except:
            data['Actual_closure_date'] = "-"

    return result


def get_all_judicial_proceedings_list():
    result = list(db.proceedingsMaster.find({'$and': [{'Type': 2}, {'Client_closed': {'$exists': False}}]}))
    for data in result:
        try:
            data['Base_date'] = date_to_IST_format(data['Base_date'])
        except:
            data['Base_date'] = "-"
        try:
            data['Closure_date'] = date_to_IST_format(data['Closure_date'])
        except:
            data['Closure_date'] = "-"
        try:
            data['Event_actual_date'] = date_to_IST_format(data['Event_actual_date'])
        except:
            data['Event_actual_date'] = "-"
        try:
            data['Actual_closure_date'] = date_to_IST_format(data['Actual_closure_date'])
        except:
            data['Actual_closure_date'] = "-"

    return result


def get_all_regular_proceedings_list():
    result = list(db.proceedingsMaster.find({'$and': [{'Type': 1}, {'Client_closed': {'$exists': False}}]}))
    for data in result:
        try:
            data['Base_date'] = date_to_IST_format(data['Base_date'])
        except:
            data['Base_date'] = "-"
        try:
            data['Closure_date'] = date_to_IST_format(data['Closure_date'])
        except:
            data['Closure_date'] = "-"
        try:
            data['Event_actual_date'] = date_to_IST_format(data['Event_actual_date'])
        except:
            data['Event_actual_date'] = "-"
        try:
            data['Actual_closure_date'] = date_to_IST_format(data['Actual_closure_date'])
        except:
            data['Actual_closure_date'] = "-"

    return result


def add_proceedings_data_in_db(data_dict):
    x = db.proceedingsMaster.insert_one(data_dict)
    return x


def get_proc_details(r_id):
    result = list(db.proceedingsMaster.find({"_id": ObjectId(r_id)}))
    if result:
        return result[0]
    else:
        return []


def get_proc_for_event_details(r_id):
    result = list(db.proceedingsMaster.find({"_id": ObjectId(r_id)}))
    if result:
        for data in result:
            try:
                data['Base_date'] = date_to_IST_format(data['Base_date'])
            except:
                data['Base_date'] = "-"
            try:
                data['Closure_date'] = date_to_IST_format(data['Closure_date'])
            except:
                data['Closure_date'] = "-"
            try:
                data['Event_actual_date'] = date_to_IST_format(data['Event_actual_date'])
            except:
                data['Event_actual_date'] = "-"
            try:
                data['Actual_closure_date'] = date_to_IST_format(data['Actual_closure_date'])
            except:
                data['Actual_closure_date'] = "-"

        return result[0]
    else:
        return []


def get_event_details_further_proc(r_id):
    return list(db.proceedingsEventMaster.find({"Proceeding_id": r_id}))


def get_event_details(r_id):
    result = list(db.proceedingsEventMaster.find({"Proceeding_id": r_id}))
    for data in result:
        try:
            data['Event_date'] = date_to_IST_format(data['Event_date'])
        except:
            data['Event_date'] = "-"
        try:
            data['Event_actual_date'] = date_to_IST_format(data['Event_actual_date'])
        except:
            data['Event_actual_date'] = "-"
        try:
            data['Event_next_date'] = date_to_IST_format(data['Event_next_date'])
        except:
            data['Event_next_date'] = "-"

    return result


def get_ay_list():
    today_date = datetime.now()
    current_year = today_date.year
    start_year = 2008
    ay_list = []
    ay_list.append('VARIOUS / OTHERS')
    while start_year != current_year + 1:
        temp = str(start_year) + '-' + str(start_year + 1)
        start_year += 1
        ay_list.append(temp)

    return ay_list[::-1]


def add_further_proc_record(data_dict, r_id):
    # check if exists in db
    exists_result = list(db.proceedingsMaster.find({"_id": ObjectId(r_id), "Status": {"$ne": "Completed"}},
                                                   {"_id": 1}))

    if exists_result:
        record_id = exists_result[0]['_id']
        x = db.proceedingsMaster.update_one({"_id": record_id}, {"$set": data_dict})
    else:
        x = None
        print('not updated')
    return x


def add_further_proc_file_record(file_data, r_id):
    result = db.proceedingsMaster.update_one({'_id': ObjectId(r_id)}, {"$set": file_data})


def get_group_name_from_client_name(c_name):
    result = list(db.clientMaster.find({'Name': c_name}, {'Group_name': 1}))
    if result:
        return result[0]['Group_name']
    return 'NA'


def get_client_code_from_name(name):
    clientMaster_result = list(db.clientMaster.find({'Name': name}, {'Client_code': 1}))
    if clientMaster_result:
        return clientMaster_result[0]['Client_code']
    else:
        return ''


def update_proc_details(r_id, data_dict):
    result = db.proceedingsMaster.update_one({'_id': ObjectId(r_id)}, {"$set": data_dict})


def add_event_details(data_dict):
    return db.proceedingsEventMaster.insert_one(data_dict)


def get_party_name_from_name(name):
    clientMaster_result = list(db.clientMaster.find({'Name': name}, {'Party_name': 1}))
    if clientMaster_result:
        return clientMaster_result[0]['Party_name']
    else:
        return ''


def live_board_proceedings_list():
    result = list(db.proceedingsMaster.aggregate([{"$match": {"Status": "", "Closure_date": {"$ne": "", "$exists": True}}},
                                                  {"$project": {"_id": 1, "Closure_date": {"$dateFromString": {
                                                      "dateString": "$Closure_date",
                                                      "format": "%Y-%m-%d"}},
                                                                "Name": 1, "AY": 1, "Description": 1,
                                                                "Section": 1, "Closure_remarks": 1,
                                                                "In_past": {"$cond": [{"$gte": ["$Closure_date",
                                                                                                datetime.now()]},
                                                                                      "No", "Yes"]}}},
                                                  {"$sort": {"Closure_date": 1}},
                                                  {"$project": {"_id": 1, "Name": 1, "AY": 1, "Description": 1,
                                                                "Section": 1, "Closure_remarks": 1,
                                                                "Closure_date": 1,
                                                                "In_past": {"$cond": [{"$gte": ["$Closure_date",
                                                                                                datetime.now()]},
                                                                                      "No", "Yes"]}}},
                                                  ]))

    return result


