import ssl
import pymongo as pymongo
from django.shortcuts import render
from . import database


# Create your views here.


def landing(request):
    all_client_list = database.get_all_clients_details()
    other_forms_list = database.get_all_other_forms_list()
    otherForms_description_list = database.initialise_description_id_mapping()
    return render(request, 'landing_otherForms.html', {'Client_list': all_client_list, 'Other_forms_list': other_forms_list,
                                                       'Other_forms_desc': otherForms_description_list})


def submit_certificate(request):
    client_name = request.POST.get('Client_Name')
    group_name = request.POST.get('Group_Name')
    client_code = request.POST.get('Client_Code')
    accepted_by = request.POST.get('Accepted_By')
    acceptance_date = request.POST.get('Acceptance_Date')
    description = request.POST.get('Description')
    # check if description value is valid
    check_description = database.get_id_from_other_from_description_name(description)
    if check_description:
        data_dict = {
            'Name': client_name.upper(),
            'Group_name': group_name.upper(),
            'Client_code': client_code,
            'Accepted_by': accepted_by.upper(),
            'Acceptance_date': acceptance_date,
            'Description': description.upper()
        }
        result = database.add_other_forms_data_in_db(data_dict)
    all_client_list = database.get_all_clients_details()
    otherForms_description_list = database.initialise_description_id_mapping()
    cert_list = database.get_all_other_forms_list()
    return render(request, 'landing_otherForms.html', {'Client_list': all_client_list, 'Other_forms_list': cert_list,
                                                       'Other_forms_desc': otherForms_description_list})


def further_other_forms_info(request, id):
    exist_result = database.get_other_forms_details(id)
    if exist_result:
        return render(request, 'further_other_forms_info.html', {'Data_Dict': exist_result})
    all_client_list = database.get_all_clients_details()
    cert_list = database.get_all_other_forms_list()
    otherForms_description_list = database.initialise_description_id_mapping()
    return render(request, 'landing_otherForms.html', {'Client_list': all_client_list, 'Other_forms_list': cert_list,
                                                       'Other_forms_desc': otherForms_description_list})


def further_other_forms_submit(request):
    save_bool = request.POST.get('save_fur', True)
    if save_bool == 'false':
        save_bool_final = False
    else:
        save_bool_final = True
    handled_by = request.POST.get('Handled_By')
    checked_by = request.POST.get('Checked_By')
    date_of_certificate = request.POST.get('Date_of_Document')
    signed_by = request.POST.get('Concluded_By')
    remarks = request.POST.get('Remarks')
    r_id = request.POST.get('Record_Id')
    ref_id = request.POST.get('Reference_No')
    data_dict = {
        'Handled_by': handled_by.upper(),
        'Checked_by': checked_by.upper(),
        'Date_of_document': date_of_certificate,
        'Concluded_by': signed_by.upper(),
        'Remarks': remarks.upper(),
        'Reference_no': ref_id.upper(),
        'Status': 'Completed' if save_bool_final else 'Inprogress'
    }

    result = database.add_further_other_forms_record(data_dict, r_id)
    cert_list = database.get_all_other_forms_list()
    all_client_list = database.get_all_clients_details()
    otherForms_description_list = database.initialise_description_id_mapping()

    return render(request, 'landing_otherForms.html', {'Client_list': all_client_list, 'Other_forms_list': cert_list,
                                                       'Other_forms_desc': otherForms_description_list})


