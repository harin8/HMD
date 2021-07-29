import pymongo
from bson import ObjectId

__MONGO_CONNECTION_URI__ = 'mongodb://localhost/'

client = pymongo.MongoClient(__MONGO_CONNECTION_URI__, 27017)
db = client.HMD


def add_contact_details(data_list):
    return db.contactMaster.insert_many(data_list)


def get_all_contact_details(id=True):
    if id:
        return list(db.contactMaster.find({}))
    return list(db.contactMaster.find({}, {'_id': 0}))


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


def check_if_contact_name_exists(name):
    result = list(db.contactMaster.find({'Name': name}))
    if len(result) >= 2:
        return True
    return False


def update_contact_details(r_id, temp):
    result = db.contactMaster.update({'_id': ObjectId(r_id)}, temp)


def get_contact_phone_email_from_name(name):
    contact_designation = list(db.contactMaster.find({'Name': name}))
    if contact_designation:
        return contact_designation[0]
    return ''


def update_contact_details_in_clientMaster(r_id, data):
    result = list(db.clientMaster.find({'Contact_details.r_id': ObjectId(r_id)}, {'_id': 0,
                                                                                  'Client_code': 1,
                                                                                  'Contact_details.$': 1}))
    if result:
        for data_db in result:
            for contact_db in data_db['Contact_details']:
                if ObjectId(contact_db['r_id']) == ObjectId(r_id):
                    contact_db['r_id'] = ObjectId(r_id)
                    contact_db['Email'] = data['Email']
                    contact_db['Contact_no'] = data['Contact_no']
                    contact_db['Remarks'] = data['Remarks']
                    # update with new contact data
                    update_data = db.clientMaster.update_one({'Client_code': data_db['Client_code'],
                                                              'Contact_details.r_id': ObjectId(r_id)},
                                                             {'$set': {'Contact_details.$': contact_db}})
                    break


