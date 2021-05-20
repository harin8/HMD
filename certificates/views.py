import ssl
import pymongo as pymongo
from django.shortcuts import render
from . import database

__MONGO_CONNECTION_URI__ = 'mongodb://localhost/'
# __MONGO_CONNECTION_URI__ = 'mongodb+srv://Dhruvang:Diwan@cluster0.xp0yp.mongodb.net/test?retryWrites=true&w
# =majority&ssl=true'

client = pymongo.MongoClient(__MONGO_CONNECTION_URI__, 27017)
# client = pymongo.MongoClient(__MONGO_CONNECTION_URI__, ssl_cert_reqs=ssl.CERT_NONE)

db = client.HMD


# Create your views here.

def landing(request):
    all_client_list = database.get_all_clients_details()
    cert_list = database.get_all_certificate_list()
    return render(request, 'landing_c.html', {'Client_list': all_client_list, 'Cert_list': cert_list})


def submit_certificate(request):
    client_name = request.POST.get('Client_Name')
    group_name = request.POST.get('Group_Name')
    client_code = request.POST.get('Client_Code')
    accepted_by = request.POST.get('Accepted_By')
    received_date = request.POST.get('Received_Date')
    description = request.POST.get('Description')

    data_dict = {
        'Name': client_name,
        'Group_name': group_name,
        'Client_code': client_code,
        'Accepted_by': accepted_by,
        'Received_date': received_date,
        'Description': description
    }
    result = database.add_certificate_data_in_db(data_dict)
    all_client_list = database.get_all_clients_details()

    cert_list = database.get_all_certificate_list()
    return render(request, 'landing_c.html', {'Client_list': all_client_list, 'Cert_list': cert_list})


def further_cert_info(request, id):
    exist_result = database.get_cert_details(id)
    if exist_result:
        return render(request, 'further_cert_info.html', {'Data_Dict': exist_result})
    all_client_list = database.get_all_clients_details()
    cert_list = database.get_all_certificate_list()
    return render(request, 'landing_c.html', {'Client_list': all_client_list, 'Cert_list': cert_list})


def further_cert_submit(request):
    handled_by = request.POST.get('Handled_By')
    checked_by = request.POST.get('Checked_By')
    date_of_certificate = request.POST.get('Date_of_Certificate')
    signed_by = request.POST.get('Signed_By')
    remarks = request.POST.get('Remarks')
    r_id = request.POST.get('Record_Id')
    data_dict = {
        'Handled_by': handled_by,
        'Checked_by': checked_by,
        'Date_of_certificate': date_of_certificate,
        'Signed_by': signed_by,
        'Remarks': remarks,
        'Status': 'Completed'
    }

    result = database.add_further_cert_record(data_dict, r_id)
    cert_list = database.get_all_certificate_list()
    all_client_list = database.get_all_clients_details()

    return render(request, 'landing_c.html', {'Client_list': all_client_list, 'Cert_list': cert_list})
