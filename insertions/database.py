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
    result = db.forumAuthorMaster.update_one({'_id': ObjectId(r_id)}, temp)


def check_if_certificate_description_exists(name):
    result = list(db.certificateDescription.find())
    if len(result) >= 1:
        for x in result:
            for i, j in x.items():
                if name == j:
                    return True
    return False


def check_if_certificate_description_exists_by_name(no):
    result = list(db.certificateDescription.find())
    if len(result) >= 1:
        for x in result:
            for i, j in x.items():
                if no == i:
                    return True
    return False


def delete_certificate_description(no):
    result = list(db.certificateDescription.find())
    for x in result:
        for i, j in x.items():
            if i == no:
                existing_id = list(db.certificateDescription.find({}, {'_id': 1}))
                db.certificateDescription.update_one({'_id': ObjectId(existing_id[0]['_id'])},
                                                    {'$unset': {i: j}})
                break


def add_certificate_description(data_list):
    result = list(db.certificateDescription.find({}, {'_id': 0}))

    if result:
        new_key = len(result[0])
        for x in data_list:
            new_key = new_key + 1
            result[0][str(new_key)] = x['Name']
        existing_id = list(db.certificateDescription.find({}, {'_id': 1}))
        db.certificateDescription.update_one({'_id': ObjectId(existing_id[0]['_id'])}, {'$set': result[0]})
    else:
        temp_dict = {}
        for x in data_list:
            max_key = 0
            new_key = max_key + 1
            temp_dict[str(new_key)] = x['Name']
        db.certificateDescription.insert_one(result)


def get_all_certificate_description(id=True):
    if id:
        return list(db.certificateDescription.find({}))
    return list(db.certificateDescription.find({}, {'_id': 0}))


def check_if_other_form_description_exists(name):
    result = list(db.otherFormsDescription.find())
    if len(result) >= 1:
        for x in result:
            for i, j in x.items():
                if name == j:
                    return True
    return False


def check_if_other_form_description_exists_by_name(no):
    result = list(db.otherFormsDescription.find())
    if len(result) >= 1:
        for x in result:
            for i, j in x.items():
                if no == i:
                    return True
    return False


def delete_other_form_description(no):
    result = list(db.otherFormsDescription.find())
    for x in result:
        for i, j in x.items():
            if i == no:
                existing_id = list(db.otherFormsDescription.find({}, {'_id': 1}))
                db.otherFormsDescription.update_one({'_id': ObjectId(existing_id[0]['_id'])},
                                                    {'$unset': {i: j}})
                break


def add_other_form_description(data_list):
    result = list(db.otherFormsDescription.find({}, {'_id': 0}))

    if result:
        new_key = len(result[0])
        for x in data_list:
            new_key = new_key + 1
            result[0][str(new_key)] = x['Name']
        existing_id = list(db.otherFormsDescription.find({}, {'_id': 1}))
        db.otherFormsDescription.update_one({'_id': ObjectId(existing_id[0]['_id'])}, {'$set': result[0]})
    else:
        temp_dict = {}
        for x in data_list:
            max_key = 0
            new_key = max_key + 1
            temp_dict[str(new_key)] = x['Name']
        db.otherFormsDescription.insert_one(result)


def get_all_other_form_description(id=True):
    if id:
        return list(db.otherFormsDescription.find({}))
    return list(db.otherFormsDescription.find({}, {'_id': 0}))


def check_if_proceedings_description_exists(name, type):
    if type == "1":
        result = list(db.regularProceedingsDescription.find())
        if len(result) >= 1:
            for x in result:
                for i, j in x.items():
                    if name == j:
                        return True
    if type == "2":
        result = list(db.judicialProceedingsDescription.find())
        if len(result) >= 1:
            for x in result:
                for i, j in x.items():
                    if name == j:
                        return True
    return False


def check_if_proceedings_description_exists_by_name(name, type):
    if type == "Regular Proceeding":
        result = list(db.regularProceedingsDescription.find())
        if len(result) >= 1:
            for x in result:
                for i, j in x.items():
                    if name == i:
                        return True
    if type == "Judicial Proceeding":
        result = list(db.judicialProceedingsDescription.find())
        if len(result) >= 1:
            for x in result:
                for i, j in x.items():
                    if name == i:
                        return True
    return False


def delete_proceedings_description(no, type):
    if type == "Regular Proceeding":
        rp_result = list(db.regularProceedingsDescription.find())
        for x in rp_result:
            for i, j in x.items():
                if i == no:
                    existing_id = list(db.regularProceedingsDescription.find({}, {'_id': 1}))
                    db.regularProceedingsDescription.update_one({'_id': ObjectId(existing_id[0]['_id'])},
                                                                {'$unset': {i: j}})
                    break

    if type == "Judicial Proceeding":
        jp_result = list(db.judicialProceedingsDescription.find())
        for x in jp_result:
            for i, j in x.items():
                if i == no:
                    existing_id = list(db.judicialProceedingsDescription.find({}, {'_id': 1}))
                    db.judicialProceedingsDescription.update_one({'_id': ObjectId(existing_id[0]['_id'])},
                                                                 {'$unset': {i: j}})
                    break


def add_proceedings_description(data_list):
    rp_result = list(db.regularProceedingsDescription.find({}, {'_id': 0}))
    jp_result = list(db.judicialProceedingsDescription.find({}, {'_id': 0}))

    if rp_result:
        new_key = len(rp_result[0])
        for x in data_list:
            if x['Type'] == "1":
                new_key = new_key + 1
                rp_result[0][str(new_key)] = x['Name']
        existing_id = list(db.regularProceedingsDescription.find({}, {'_id': 1}))
        db.regularProceedingsDescription.update_one({'_id': ObjectId(existing_id[0]['_id'])}, {'$set': rp_result[0]})
    else:
        temp_dict = {}
        for x in data_list:
            if x['Type'] == "1":
                max_key = 0
                new_key = max_key + 1
                temp_dict[str(new_key)] = x['Name']
        db.regularProceedingsDescription.insert_one(rp_result)

    if jp_result:
        new_key = len(jp_result[0])
        for x in data_list:
            if x['Type'] == "2":
                new_key = new_key + 1
                jp_result[0][str(new_key)] = x['Name']
        existing_id = list(db.judicialProceedingsDescription.find({}, {'_id': 1}))
        db.judicialProceedingsDescription.update_one({'_id': ObjectId(existing_id[0]['_id'])}, {'$set': jp_result[0]})
    else:
        temp_dict = {}
        for x in data_list:
            if x['Type'] == "2":
                max_key = 0
                new_key = max_key + 1
                temp_dict[str(new_key)] = x['Name']
        db.judicialProceedingsDescription.insert_one(jp_result)


def get_all_proceedings_description(id=True):
    final_result = []
    if id:
        rp_result = list(db.regularProceedingsDescription.find({}))
        jp_result = list(db.judicialProceedingsDescription.find({}))
    else:
        rp_result = list(db.regularProceedingsDescription.find({}, {'_id': 0}))
        jp_result = list(db.judicialProceedingsDescription.find({}, {'_id': 0}))
    if not rp_result:
        return []
    if not jp_result:
        return []
    for x in rp_result:
        for key, value in x.items():
            temp_dict = {'Type': 'Regular Proceeding', 'Name': value, 'Sr_no': key}
            final_result.append(temp_dict)
    for x in jp_result:
        for key, value in x.items():
            temp_dict = {'Type': 'Judicial Proceeding', 'Name': value, 'Sr_no': key}
            final_result.append(temp_dict)

    return final_result


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
