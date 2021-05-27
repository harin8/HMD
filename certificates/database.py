import ssl
import pymongo
from bson.objectid import ObjectId

# __MONGO_CONNECTION_URI__ = 'mongodb://localhost/'

__MONGO_CONNECTION_URI__ = 'mongodb+srv://Dhruvang:Diwan@cluster0.xp0yp.mongodb.net/test?retryWrites=true&w=majority&ssl=true'

# client = pymongo.MongoClient(__MONGO_CONNECTION_URI__, 27017)
client = pymongo.MongoClient(__MONGO_CONNECTION_URI__, ssl_cert_reqs=ssl.CERT_NONE)
db = client.HMD


def initialise_description_id_mapping():
    return {'1': 'NETWORTH', '2': 'TURNOVER', '3': 'WORKING CAPITAL', '4': 'INCOME SOURCE', '5': 'DEBTORS AGING',
            '6': 'CREDITORS AGING', '7': 'FORM 15CB', '8': 'NO DUES', '9': 'IMPORT / EXPORT OBLIGATION',
            '10': 'EXEMPTIONS / DEDUCTIONS', '11': 'BANK FINANCE', '12': 'VISA PURPOSE', '13': 'COMPANY LAW',
            '14': 'LLP LAW', '15': 'RERA LAW', '16': 'FEMA LAW', '17': 'TRUST LAW', '18': 'MSME LAW',
            '19': 'BANK KYC CERTIFICATE', '20': 'BANK AUDIT', '21': 'OTHERS'}


def get_certificate_description_name_from_id(description_id):
    temp_dict = initialise_description_id_mapping()
    try:
        return temp_dict[str(description_id)]
    except:
        return 'OTHERS'


def get_id_from_certificate_description_name(description):
    temp_dict = initialise_description_id_mapping()
    for key, value in temp_dict.items():
        if value == description:
            return key
    return '21'


def get_all_clients_details():
    return list(db.clientMaster.find({}, {'_id': 0, 'Client_no': 0}))


def get_all_certificate_list():
    return list(db.certificateMaster.find({}))


def add_certificate_data_in_db(data_dict):
    x = db.certificateMaster.insert_one(data_dict)
    return x


def get_cert_details(r_id):
    result = list(db.certificateMaster.find({"_id": ObjectId(r_id)}))
    if result:
        return result[0]
    else:
        return []


def add_further_cert_record(data_dict, r_id):
    # check if exists in db
    exists_result = list(db.certificateMaster.find({"_id": ObjectId(r_id), "Status": {"$ne": "Completed"}},
                                                   {"_id": 1}))

    if exists_result:
        record_id = exists_result[0]['_id']
        x = db.certificateMaster.update_one({"_id": record_id}, {"$set": data_dict})
    else:
        x = None
        print('not updated')
    return x
