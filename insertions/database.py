import bcrypt
import pymongo
from bson import ObjectId

__MONGO_CONNECTION_URI__ = 'mongodb://localhost/'

client = pymongo.MongoClient(__MONGO_CONNECTION_URI__, 27017)
db = client.HMD


def add_forum_author_details(data_list):
    return db.forumAuthorMaster.insert_many(data_list)


def get_all_forum_author_details(id=True):
    if id:
        return list(db.forumAuthorMaster.find({}))
    return list(db.forumAuthorMaster.find({}, {'_id': 0}))


def get_contact_detail_from_id(id):
    result = list(db.forumAuthorMaster.find({'_id': ObjectId(id)}))
    if result:
        return result[0]
    return None


def get_contact_detail_from_name_no(name, no):
    result = list(db.forumAuthorMaster.find({'Name': name, 'Contact_no': no}))
    if result:
        return result
    return None


def check_if_contact_name_exists(name):
    result = list(db.forumAuthorMaster.find({'Name': name}))
    if len(result) >= 1:
        return True
    return False


def update_contact_details(r_id, temp):
    result = db.forumAuthorMaster.update({'_id': ObjectId(r_id)}, temp)


def get_contact_phone_email_from_name(name):
    contact_designation = list(db.forumAuthorMaster.find({'Name': name}))
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
                    contact_db['Name'] = data['Name']
                    # update with new contact data
                    update_data = db.clientMaster.update_one({'Client_code': data_db['Client_code'],
                                                              'Contact_details.r_id': ObjectId(r_id)},
                                                             {'$set': {'Contact_details.$': contact_db}})
                    break


def verify_password(operation_name, entered_password):
    stored_salt_result = db.credentials.find_one({'Operation': "Salt"}, {"Salt": 1})
    if stored_salt_result:
        stored_salt = stored_salt_result['Salt']
        stored_hashed_password_result = db.credentials.find_one({'Operation': operation_name}, {"Password": 1})
        if stored_hashed_password_result:
            stored_password_hashed = stored_hashed_password_result['Password']
            entered_password_hashed = bcrypt.hashpw(entered_password.encode('utf-8'), stored_salt)
            if entered_password_hashed == stored_password_hashed:
                return True
            else:
                return False
        else:
            return False
    else:
        return False