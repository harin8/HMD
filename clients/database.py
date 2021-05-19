import ssl
import pymongo

# __MONGO_CONNECTION_URI__ = 'mongodb://localhost/'
__MONGO_CONNECTION_URI__ = 'mongodb+srv://Dhruvang:Diwan@cluster0.xp0yp.mongodb.net/test?retryWrites=true&w=majority&ssl=true'


# client = pymongo.MongoClient(__MONGO_CONNECTION_URI__, 27017)
client = pymongo.MongoClient(__MONGO_CONNECTION_URI__, ssl_cert_reqs=ssl.CERT_NONE)
db = client.HMD


def get_client_master_list():
    result = list(db.clientMaster.find({}, {'_id': 0}))
    return result


def get_all_distinct_value(field_name):
    result = db.clientMaster.distinct(field_name)
    return result


def add_client_details(data_dict):
    return db.clientMaster_temp.insert(data_dict)
