import ssl
import pymongo
from bson import ObjectId

# __MONGO_CONNECTION_URI__ = 'mongodb://localhost/'
__MONGO_CONNECTION_URI__ = 'mongodb+srv://Dhruvang:Diwan@cluster0.xp0yp.mongodb.net/test?retryWrites=true&w=majority&ssl=true'


# client = pymongo.MongoClient(__MONGO_CONNECTION_URI__, 27017)
client = pymongo.MongoClient(__MONGO_CONNECTION_URI__, ssl_cert_reqs=ssl.CERT_NONE)
db = client.HMD


def add_contact_details(data_list):
    return db.contactMaster.insert_many(data_list)


def get_all_contact_details():
    return list(db.contactMaster.find({}))


def get_contact_detail_from_id(id):
    result = list(db.contactMaster.find({'_id': ObjectId(id)}))
    if result:
       return result[0]
    return None


def get_contact_detail_from_name_no(name, no):
    result = list(db.contactMaster.find({'Name': name, 'Contact_no': no}))
    if result:
        return result
    return None


def update_contact_details(r_id, temp):
    result = db.contactMaster.update({'_id': ObjectId(r_id)}, temp)