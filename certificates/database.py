import ssl
import pymongo
from bson.objectid import ObjectId

# __MONGO_CONNECTION_URI__ = 'mongodb://localhost/'

__MONGO_CONNECTION_URI__ = 'mongodb+srv://Dhruvang:Diwan@cluster0.xp0yp.mongodb.net/test?retryWrites=true&w=majority&ssl=true'

# client = pymongo.MongoClient(__MONGO_CONNECTION_URI__, 27017)
client = pymongo.MongoClient(__MONGO_CONNECTION_URI__, ssl_cert_reqs=ssl.CERT_NONE)
db = client.HMD


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
