import pymongo as pymongo
from django.shortcuts import render
from accounts.decorators import permission_required
from . import database
from django.core.files.storage import FileSystemStorage
import datetime
from datetime import datetime
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
import clients.database as client_database

# Create your views here.

@permission_required('other_forms', 'view')
def landing(request):
    all_client_list = database.get_all_clients_details()
    other_forms_list = database.get_all_other_forms_list()
    for data in other_forms_list:
        data['Client_code'] = database.get_client_code_from_name(data['Name'])
        data['Group_name'] = database.get_group_name_from_client_name(data['Name'])
        try:
            data['Acceptance_date'] = database.ymd_str_to_IST_format(data['Acceptance_date'])
        except Exception:
            pass
        try:
            data['Date_of_document'] = database.ymd_str_to_IST_format(data['Date_of_document'])
        except Exception:
            pass
    otherForms_description_list = database.initialise_description_id_mapping()
    return render(request, 'landing_otherForms.html', {'Client_list': all_client_list, 'Other_forms_list': other_forms_list,
                                                       'Other_forms_desc': otherForms_description_list})


@permission_required('other_forms', 'add')
def submit_certificate(request):
    client_name = request.POST.get('Client_Name')
    client_code = request.POST.get('Client_Code')
    accepted_by = request.POST.get('Accepted_By')
    acceptance_date = request.POST.get('Acceptance_Date')
    description = request.POST.get('Description')
    # check if client name is valid
    valid_client, db_client_name = database.check_client_from_client_code(client_code)
    # check if description value is valid
    check_description = database.get_id_from_other_from_description_name(description)
    if check_description and valid_client:
        data_dict = {
            'Name': db_client_name,
            'Accepted_by': accepted_by.upper(),
            'Acceptance_date': acceptance_date,
            'Description': description.upper(),
            'File': 0
        }
        result = database.add_other_forms_data_in_db(data_dict)
    all_client_list = database.get_all_clients_details()
    otherForms_description_list = database.initialise_description_id_mapping()
    other_forms_list = database.get_all_other_forms_list()
    for data in other_forms_list:
        data['Client_code'] = database.get_client_code_from_name(data['Name'])
        data['Group_name'] = database.get_group_name_from_client_name(data['Name'])
    return render(request, 'landing_otherForms.html', {'Client_list': all_client_list, 'Other_forms_list': other_forms_list,
                                                       'Other_forms_desc': otherForms_description_list})


@permission_required('other_forms', 'view')
def further_other_forms_info(request, id):
    exist_result = database.get_other_forms_details(id)
    exist_result['Client_code'] = database.get_client_code_from_name(exist_result['Name'])
    exist_result['Group_name'] = database.get_group_name_from_client_name(exist_result['Name'])
    if exist_result:
        return render(request, 'further_other_forms_info.html', {'Data_Dict': exist_result})
    all_client_list = database.get_all_clients_details()
    other_forms_list = database.get_all_other_forms_list()
    otherForms_description_list = database.initialise_description_id_mapping()
    for data in other_forms_list:
        data['Client_code'] = database.get_client_code_from_name(data['Name'])
        data['Group_name'] = database.get_group_name_from_client_name(data['Name'])
    return render(request, 'landing_otherForms.html', {'Client_list': all_client_list, 'Other_forms_list': other_forms_list,
                                                       'Other_forms_desc': otherForms_description_list})


@permission_required('other_forms', 'add')
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
    other_forms_list = database.get_all_other_forms_list()
    for data in other_forms_list:
        data['Client_code'] = database.get_client_code_from_name(data['Name'])
        data['Group_name'] = database.get_group_name_from_client_name(data['Name'])
    all_client_list = database.get_all_clients_details()
    otherForms_description_list = database.initialise_description_id_mapping()

    return render(request, 'landing_otherForms.html', {'Client_list': all_client_list, 'Other_forms_list': other_forms_list,
                                                       'Other_forms_desc': otherForms_description_list})


@permission_required('other_forms', 'add')
def submit_otherform_File(request):
    r_id = request.POST.get('Record_Id')
    if request.FILES['myfile']:
        data_dict = {
            'File': 1
        }
        data_update = database.update_otherform_details(r_id, data_dict)
        myfile = request.FILES['myfile']
        now = datetime.now()
        date_time = now.strftime("%m%d%Y%H%M%S")
        only_file_name = myfile.name.rsplit('.', 1)[0] + date_time
        file = only_file_name + "." + myfile.name.rsplit('.', 1)[1]
        file_data = {
            'File_name': file
        }
        file_update = database.add_further_otherform_file_record(file_data, r_id)
        fs = FileSystemStorage()
        filename = fs.save(file, myfile)
        uploaded_file_url = fs.url(file)
    return further_other_forms_info(request, r_id)


def pdf_view(request, id):
    fs = FileSystemStorage()
    exist_result = database.get_other_forms_details(id)
    filename = exist_result['File_name']
    if fs.exists(filename):
        with fs.open(filename) as pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            # response['Content-Disposition'] = 'attachment; filename="mypdf.pdf"' #user will be prompted with the browser’s open/save file
            response[
                'Content-Disposition'] = 'inline; filename="KARAN03132022015234.pdf"'  # user will be prompted display the PDF in the browser
            return response
    else:
        return HttpResponseNotFound('The requested pdf was not found.')


@permission_required('other_forms', 'delete')
def delete_other_forms(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        id = request.POST.get('otherFormId')
        if client_database.verify_password("Record Delete", password): 
            if database.delete_other_forms_record(id):
                return JsonResponse({'status': 'success', 'message': 'Record deleted successfully.'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Record not found.'}, status=404)
        else:
            return JsonResponse({'status': 'error', 'message': 'Incorrect password.'}, status=403)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)
