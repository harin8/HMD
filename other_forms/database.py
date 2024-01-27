import pymongo
from bson.objectid import ObjectId
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


def check_client_from_client_code(client_code):
    result = list(db.clientMaster.find({'Client_code': client_code}, {'_id': 1, 'Name': 1}))
    if result:
        return True, result[0]['Name']
    return False, ''


def get_all_clients_details():
    return list(db.clientMaster.find({}, {'_id': 0, 'Client_no': 0, 'Contact_details.r_id': 0}))


def get_all_other_forms_list():
    return list(db.otherFormsMaster.find({'Client_closed': {'$exists': False}}))


def add_other_forms_data_in_db(data_dict):
    x = db.otherFormsMaster.insert_one(data_dict)
    return x


def get_other_forms_details(r_id):
    result = list(db.otherFormsMaster.find({"_id": ObjectId(r_id)}))
    if result:
        return result[0]
    else:
        return []


def initialise_description_id_mapping():
    result = list(db.otherFormsDescription.find({}, {'_id': 0}))

    if result:
        return result[0]


def get_id_from_other_from_description_name(description):
    temp_dict = initialise_description_id_mapping()
    for key, value in temp_dict.items():
        if value == description:
            return True
    return False


def add_further_other_forms_record(data_dict, r_id):
    # check if exists in db
    exists_result = list(db.otherFormsMaster.find({"_id": ObjectId(r_id), "Status": {"$ne": "Completed"}},
                                                   {"_id": 1}))

    if exists_result:
        record_id = exists_result[0]['_id']
        x = db.otherFormsMaster.update_one({"_id": record_id}, {"$set": data_dict})
    else:
        x = None
        print('not updated')
    return x


def insert_description_to_db():
    temp = {"1": "ITA_FORM 15CA",
            "2": "ITA_FORM 26QB",
            "3": "ITA_FORM 15G / 15H_NO TDS",
            "4": "ITA_FORM 13_LOWER TDS",
            "5": "ITA_FORM 49A/49AA_PAN APPLICATION / CORRECTION",
            "6": "ITA_FORM 49B_TAN APPLICATION / CORRECTION",
            "7": "ITA_FORM 10BD_STATEMENT U/S. 80G / 35",
            "8": "ITA_FORM 10A_REG U/S. 10(23C)1(i)/(iv)",
            "9": "ITA_FORM 10A_REG U/S. 12A(1)(ac)(i)/(vi)",
            "10": "ITA_FORM 10A_REG U/S. 80G(5)1(i)/(iv)",
            "11": "ITA_FORM 10AB_REG U/S. 10(23C)1(ii)/(iii)",
            "12": "ITA_FORM 10AB_REG U/S. 12A(1)(ac)(ii)/(iii)/(iv)/(v)",
            "13": "ITA_FORM 10AB_REG U/S. 80G(5)1(iI)/(iii)",
            "14": "ITA_APPLICATION U/S. 17(2)",
            "15": "ITA_APPLICATION U/S. 17(2)",
            "16": "ITA_BUSINESS DISCONTINUANCE NOTICE U/S. 176",
            "17": "ITA_REVISION APPLICATION U/S. 264",
            "18": "ITA_FORM 35_APPEAL TO CIT(A)",
            "19": "ITA_FORM 36_APPEAL TO ITAT",
            "20": "ITA_FORM 36A_CO TO ITAT",
            "21": "ITA_MA TO ITAT",
            "22": "ITA_STAY APP. BEFORE PCCIT/CCIT/PCIT",
            "23": "ITA_STAY APP. BEFORE CIT(A)",
            "24": "ITA_STAY APP. BEFORE ITAT",
            "25": "HC WRIT / APPEAL / OTHER MATTER",
            "26": "SC WRIT / APPEAL / OTHER MATTER",
            "27": "SET ASIDE TO COMMISSIONER(APPEALS)",
            "28": "SET ASIDE TO APPELLATE TRIBUNAL",
            "29": "JEWELLERY / SEIZED MATERIAL RELEASE",
            "31": "FCRA_FC-3_RENEWAL",
            "32": "FCRA_FC-4_ANNUAL RETURN",
            "33": "PARTNERSHIP DEED (NEW)",
            "34": "ADMISSION CUM PARTNERSHIP DEED",
            "35": "RETIREMENT CUM PARTNERSHIP DEED",
            "36": "DISSOLUTION DEED",
            "37": "LLP AGREEMENT",
            "38": "SUPPLEMENTARY DEED / AGREEMENT",
            "39": "RENT / LEASE AGREEMENT",
            "40": "TRUST DEED",
            "41": "FIRM REGISTRATION",
            "42": "OTHER PARTNERSHIP FIRM MATTER",
            "43": "LLP REGISTRATION",
            "44": "COMPANY REGISTRATION",
            "45": "MSME REGISTRATION",
            "46": "GST REGISTRATION",
            "47": "IEC REGISTRATION",
            "48": "EL_FORM 1_STATEMENT",
            "49": "EL_FORM 3_APPEAL TO CIT(A)",
            "50": "EL_FORM 4_APPEAL TO ITAT",
            "51": "BLACK MONEY_FORM 2_APPEAL TO CIT(A)",
            "52": "BLACK MONEY_FORM 3_APPEAL TO ITAT",
            "53": "BLACK MONEY_FORM 4_CO TO ITAT",
            "54": "BENAMI_FORM 3_APPEAL TO PBPT-AT",
            "55": "DISCLOSURE SCHEME",
            "56": "SETTLEMENT SCHEME",
            "57": "ADVISORY",
            "58": "OTHERS"}
    db.otherFormsDescription.insert(temp)


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