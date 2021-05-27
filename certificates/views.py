import ssl
import pymongo as pymongo
from django.shortcuts import render
from . import database

# Create your views here.


def landing(request):
    all_client_list = database.get_all_clients_details()
    cert_list = database.get_all_certificate_list()
    certificate_description_list = database.initialise_description_id_mapping()
    return render(request, 'landing_c.html', {'Client_list': all_client_list, 'Cert_list': cert_list,
                                              'Cert_Desc': certificate_description_list})


def submit_certificate(request):
    client_name = request.POST.get('Client_Name')
    group_name = request.POST.get('Group_Name')
    client_code = request.POST.get('Client_Code')
    accepted_by = request.POST.get('Accepted_By')
    received_date = request.POST.get('Received_Date')
    description = request.POST.get('Description')
    #check if description value is valid
    check_description = database.get_id_from_certificate_description_name(description)
    if check_description:
        data_dict = {
            'Name': client_name.upper(),
            'Group_name': group_name.upper(),
            'Client_code': client_code,
            'Accepted_by': accepted_by.upper(),
            'Received_date': received_date,
            'Description': description.upper()
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
        'Handled_by': handled_by.upper(),
        'Checked_by': checked_by.upper(),
        'Date_of_certificate': date_of_certificate,
        'Signed_by': signed_by.upper(),
        'Remarks': remarks.upper(),
        'Status': 'Completed'
    }

    result = database.add_further_cert_record(data_dict, r_id)
    cert_list = database.get_all_certificate_list()
    all_client_list = database.get_all_clients_details()

    return render(request, 'landing_c.html', {'Client_list': all_client_list, 'Cert_list': cert_list})


