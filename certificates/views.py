from django.shortcuts import render
from . import database

# Create your views here.


def landing(request):
    all_client_list = database.get_all_clients_details()
    cert_list = database.get_all_certificate_list()
    for data in cert_list:
        data['Client_code'] = database.get_client_code_from_name(data['Name'])
        data['Group_name'] = database.get_group_name_from_client_name(data['Name'])
    certificate_description_list = database.initialise_description_id_mapping()
    return render(request, 'landing_c.html', {'Client_list': all_client_list, 'Cert_list': cert_list,
                                              'Cert_Desc': certificate_description_list})


def submit_certificate(request):
    client_name = request.POST.get('Client_Name')
    accepted_by = request.POST.get('Accepted_By')
    client_code = request.POST.get('Client_Code')
    acceptance_date = request.POST.get('Acceptance_Date')
    description = request.POST.get('Description')
    # check if client name is valid
    valid_client, db_client_name = database.check_client_from_client_code(client_code)
    #check if description value is valid
    check_description = database.get_id_from_certificate_description_name(description)
    if check_description and valid_client:
        data_dict = {
            'Name': db_client_name,
            'Accepted_by': accepted_by.upper(),
            'Acceptance_date': acceptance_date,
            'Description': description.upper()
        }
        result = database.add_certificate_data_in_db(data_dict)
    all_client_list = database.get_all_clients_details()
    certificate_description_list = database.initialise_description_id_mapping()
    cert_list = database.get_all_certificate_list()
    for data in cert_list:
        data['Client_code'] = database.get_client_code_from_name(data['Name'])
        data['Group_name'] = database.get_group_name_from_client_name(data['Name'])
    return render(request, 'landing_c.html', {'Client_list': all_client_list, 'Cert_list': cert_list,
                                              'Cert_Desc': certificate_description_list})


def further_cert_info(request, id):
    exist_result = database.get_cert_details(id)
    exist_result['Client_code'] = database.get_client_code_from_name(exist_result['Name'])
    exist_result['Group_name'] = database.get_group_name_from_client_name(exist_result['Name'])
    if exist_result:
        return render(request, 'further_cert_info.html', {'Data_Dict': exist_result})
    all_client_list = database.get_all_clients_details()
    cert_list = database.get_all_certificate_list()
    for data in cert_list:
        data['Client_code'] = database.get_client_code_from_name(data['Name'])
        data['Group_name'] = database.get_group_name_from_client_name(data['Name'])
    certificate_description_list = database.initialise_description_id_mapping()
    return render(request, 'landing_c.html', {'Client_list': all_client_list, 'Cert_list': cert_list,
                                              'Cert_Desc': certificate_description_list})


def further_cert_submit(request):
    save_bool = request.POST.get('save_fur', True)
    if save_bool == 'false':
        save_bool_final = False
    else:
        save_bool_final = True
    handled_by = request.POST.get('Handled_By')
    checked_by = request.POST.get('Checked_By')
    date_of_certificate = request.POST.get('Date_of_Certificate')
    signed_by = request.POST.get('Signed_By')
    remarks = request.POST.get('Remarks')
    r_id = request.POST.get('Record_Id')
    udin = request.POST.get('Udin')
    data_dict = {
        'Handled_by': handled_by.upper(),
        'Checked_by': checked_by.upper(),
        'Date_of_certificate': date_of_certificate,
        'Signed_by': signed_by.upper(),
        'Remarks': remarks.upper(),
        'Udin': udin.upper(),
        'Status': 'Completed' if save_bool_final else 'Inprogress'
    }

    result = database.add_further_cert_record(data_dict, r_id)
    cert_list = database.get_all_certificate_list()
    for data in cert_list:
        data['Client_code'] = database.get_client_code_from_name(data['Name'])
        data['Group_name'] = database.get_group_name_from_client_name(data['Name'])
    all_client_list = database.get_all_clients_details()
    certificate_description_list = database.initialise_description_id_mapping()
    return render(request, 'landing_c.html', {'Client_list': all_client_list, 'Cert_list': cert_list,
                                              'Cert_Desc': certificate_description_list})


