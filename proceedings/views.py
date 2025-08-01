from typing import List, Any
import os
from django.shortcuts import render
from . import database
from django.core.files.storage import FileSystemStorage
import datetime
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import clients.database as client_database
# Create your views here.


@login_required
def mark_case(request):
    """View to mark/unmark a proceedings case"""
    if request.method == 'POST':
        proceeding_id = request.POST.get('proceeding_id')
        action = request.POST.get('action')  # 'mark' or 'unmark'
        username = request.user.id
        
        if action == 'mark':
            success = database.mark_proceedings_case(proceeding_id, username)
        else:  # unmark
            success = database.unmark_proceedings_case(proceeding_id, username)
            
        return JsonResponse({'success': success})
    return JsonResponse({'success': False}, status=400)

@login_required
def landing(request):
    ay = request.GET.get('A.Y')
    ay_list = database.get_ay_list()
    all_client_list = database.get_all_clients_details()
    proc_list = database.get_all_proceedings_list()
    for data in proc_list:
        data['Client_code'] = database.get_client_code_from_name(data['Name'])
        data['Group_name'] = database.get_group_name_from_client_name(data['Name'])
    if ay:
        return render(request, 'landing_p.html',
                      {'AY_List': ay_list, 'Client_list': all_client_list, 'Proc_list': proc_list})
    else:
        return render(request, 'landing_p.html',
                      {'AY_list': ay_list, 'Client_list': all_client_list, 'Proc_list': proc_list})


def submit_proceedings(request):
    ay = request.GET.get('A.Y')
    ay_list = database.get_ay_list()
    client_name = request.POST.get('Client_Name')
    accepted_by = request.POST.get('Accepted_By')
    client_code = request.POST.get('Client_Code')
    base_Date = request.POST.get('Base_Date')
    description = request.POST.get('Description')
    section = request.POST.get('Section')
    base_Document = request.POST.get('Base_Document')
    led_By = request.POST.get('Led_By')
    AY = request.POST.get('AY')
    # check if client name is valid
    valid_client, db_client_name = database.check_client_from_client_code(client_code)

    if valid_client:
        data_dict = {
            'Name': db_client_name,
            'Base_document': base_Document.upper(),
            'Led_by': led_By.upper(),
            'Base_date': base_Date,
            'Description': description.upper(),
            'AY': AY,
            'Type': 3,
            'Section': section,
            'Submitted_ini': True,
            'Forum_bench': '',
            'Status': '',
            'Case_reference_no': '',
            'Event': 0
        }
        return_result = database.add_proceedings_data_in_db(data_dict)
    all_client_list = database.get_all_clients_details()

    ay = request.GET.get('A.Y')
    ay_list = database.get_ay_list()
    proc_list = database.get_all_proceedings_list()
    for data in proc_list:
        data['Client_code'] = database.get_client_code_from_name(data['Name'])
        data['Group_name'] = database.get_group_name_from_client_name(data['Name'])
    return render(request, 'landing_p.html',
                  {'AY_List': ay_list, 'Client_list': all_client_list, 'Proc_list': proc_list})


def judicial_proceedings_landing(request):
    ay = request.GET.get('A.Y')
    ay_list = database.get_ay_list()
    all_client_list = database.get_all_clients_details()
    proc_list = database.get_all_judicial_proceedings_list()
    certificate_description_list = database.initialise_juddescription_id_mapping()
    for data in proc_list:
        data['Client_code'] = database.get_client_code_from_name(data['Name'])
        data['Group_name'] = database.get_group_name_from_client_name(data['Name'])
    if ay:
        return render(request, 'landing_jp.html',
                      {'AY_List': ay_list, 'Client_list': all_client_list, 'Proc_list': proc_list,
                       'Cert_Desc': certificate_description_list})
    else:
        return render(request, 'landing_jp.html',
                      {'AY_list': ay_list, 'Client_list': all_client_list, 'Proc_list': proc_list,
                       'Cert_Desc': certificate_description_list})


def submit_judicial_proceedings(request):
    ay = request.GET.get('A.Y')
    ay_list = database.get_ay_list()
    client_name = request.POST.get('Client_Name')
    accepted_by = request.POST.get('Accepted_By')
    client_code = request.POST.get('Client_Code')
    base_Date = request.POST.get('Base_Date')
    description = request.POST.get('Description')
    section = request.POST.get('Section')
    base_Document = request.POST.get('Base_Document')
    led_By = request.POST.get('Led_By')
    AY = request.POST.get('AY')
    # check if client name is valid
    valid_client, db_client_name = database.check_client_from_client_code(client_code)

    if valid_client:
        data_dict = {
            'Name': db_client_name,
            'Base_document': base_Document.upper(),
            'Led_by': led_By.upper(),
            'Base_date': base_Date,
            'Description': description.upper(),
            'AY': AY,
            'Type': 2,
            'Section': section,
            'Submitted_ini': True,
            'Forum_bench': '',
            'Status': '',
            'Case_reference_no': '',
            'Event': 0
        }
        return_result = database.add_proceedings_data_in_db(data_dict)
    all_client_list = database.get_all_clients_details()

    ay = request.GET.get('A.Y')
    ay_list = database.get_ay_list()
    proc_list = database.get_all_judicial_proceedings_list()
    certificate_description_list = database.initialise_juddescription_id_mapping()
    for data in proc_list:
        data['Client_code'] = database.get_client_code_from_name(data['Name'])
        data['Group_name'] = database.get_group_name_from_client_name(data['Name'])

    if ay:
        return render(request, 'landing_jp.html',
                      {'AY_List': ay_list, 'Client_list': all_client_list, 'Proc_list': proc_list,
                       'Cert_Desc': certificate_description_list})
    else:
        return render(request, 'landing_jp.html',
                      {'AY_list': ay_list, 'Client_list': all_client_list, 'Proc_list': proc_list,
                       'Cert_Desc': certificate_description_list})


def regular_proceedings_landing(request):
    ay = request.GET.get('A.Y')
    ay_list = database.get_ay_list()
    all_client_list = database.get_all_clients_details()
    proc_list = database.get_all_regular_proceedings_list()
    certificate_description_list = database.initialise_regdescription_id_mapping()
    for data in proc_list:
        data['Client_code'] = database.get_client_code_from_name(data['Name'])
        data['Group_name'] = database.get_group_name_from_client_name(data['Name'])
    if ay:
        return render(request, 'landing_rp.html',
                      {'AY_List': ay_list, 'Client_list': all_client_list, 'Proc_list': proc_list,
                       'Cert_Desc': certificate_description_list})
    else:
        return render(request, 'landing_rp.html',
                      {'AY_list': ay_list, 'Client_list': all_client_list, 'Proc_list': proc_list,
                       'Cert_Desc': certificate_description_list})


def submit_regular_proceedings(request):
    ay_list = database.get_ay_list()
    client_name = request.POST.get('Client_Name')
    accepted_by = request.POST.get('Accepted_By')
    client_code = request.POST.get('Client_Code')
    base_Date = request.POST.get('Base_Date')
    description = request.POST.get('Description')
    section = request.POST.get('Section')
    base_Document = request.POST.get('Base_Document')
    led_By = request.POST.get('Led_By')
    AY = request.POST.get('AY')
    # check if client name is valid
    valid_client, db_client_name = database.check_client_from_client_code(client_code)

    if valid_client:
        data_dict = {
            'Name': db_client_name,
            'Base_document': base_Document.upper(),
            'Led_by': led_By.upper(),
            'Base_date': base_Date,
            'Description': description.upper(),
            'AY': AY,
            'Type': 1,
            'Section': section,
            'Submitted_ini': True,
            'Forum_bench': '',
            'Status': '',
            'Case_reference_no': '',
            'Event': 0
        }
        return_result = database.add_proceedings_data_in_db(data_dict)
    all_client_list = database.get_all_clients_details()

    ay = request.GET.get('A.Y')
    ay_list = database.get_ay_list()
    proc_list = database.get_all_regular_proceedings_list()
    certificate_description_list = database.initialise_regdescription_id_mapping()
    for data in proc_list:
        data['Client_code'] = database.get_client_code_from_name(data['Name'])
        data['Group_name'] = database.get_group_name_from_client_name(data['Name'])

    if ay:
        return render(request, 'landing_rp.html',
                      {'AY_List': ay_list, 'Client_list': all_client_list, 'Proc_list': proc_list,
                       'Cert_Desc': certificate_description_list})
    else:
        return render(request, 'landing_rp.html',
                      {'AY_list': ay_list, 'Client_list': all_client_list, 'Proc_list': proc_list,
                       'Cert_Desc': certificate_description_list})


def further_proc_info(request, id):
    exist_result = database.get_proc_details(id)
    exist_result['Client_code'] = database.get_client_code_from_name(exist_result['Name'])
    exist_result['Group_name'] = database.get_group_name_from_client_name(exist_result['Name'])
    exist_result['is_marked'] = database.is_case_marked_by_user(id, request.user.id)
    
    event = exist_result['Event']
    if exist_result:
        if event == 0:
            return render(request, 'further_proc_info.html', {'Data_Dict': exist_result})
        else:
            event_result = database.get_event_details_further_proc(id)
            return render(request, 'further_proc_info.html', {'Data_Dict': exist_result, 'Event_list': event_result})

    all_client_list = database.get_all_clients_details()
    proc_list = database.get_all_proceedings_list()
    for data in proc_list:
        data['Client_code'] = database.get_client_code_from_name(data['Name'])
        data['Group_name'] = database.get_group_name_from_client_name(data['Name'])

    return render(request, 'landing_p.html', {'Client_list': all_client_list, 'Proc_list': proc_list})


def further_proc_submit(request):
    r_id = request.POST.get('Record_Id')
    type = request.POST.get('Type')
    exist_result = database.get_proc_details(r_id)
    client_name = exist_result['Name']
    accepted_by = request.POST.get('Accepted_By')
    client_code = request.POST.get('Client_Code')
    base_Date = request.POST.get('Base_Date')
    description = request.POST.get('Description')
    section = request.POST.get('Section')
    base_Document = request.POST.get('Base_Document')
    led_By = request.POST.get('Led_By')
    AY = request.POST.get('AY')
    close_proceedings = request.POST.get('close_proceedings')
    # check if client name is valid
    valid_client, db_client_name = database.check_client_from_client_code(client_code)

    if type == "1":
        if request.POST.get('Forum_Bench') != '':
            forum_bench = request.POST.get('Forum_Bench')
        else:
            forum_bench = ''

        if request.POST.get('Case_Reference_no') != '':
            case_reference_no = request.POST.get('Case_Reference_no')
        else:
            case_reference_no = ''

        data_dict = {
            'Forum_bench': forum_bench.upper(),
            'Case_reference_no': case_reference_no.upper(),
            'Led_by': led_By.upper()
        }
        data_update = database.update_proc_details(r_id, data_dict)
        return further_proc_info(request, r_id)

    if type == "2":
        status = exist_result['Status']
        if status != 'Completed':
            closure_date = request.POST.get('Closure_Date')
            actual_closure_date = request.POST.get('Actual_Closure_Date')
            closure_type = request.POST.get('Closure_Type')
            closure_particulars = request.POST.get('Closure_Particulars')
            closure_handled_by = request.POST.get('Closure_Handled_By')
            closure_remarks = request.POST.get('Closure_Remarks')
            data_dict = {
                'Closure_date': closure_date,
                'Actual_closure_date': actual_closure_date,
                'Closure_type': closure_type,
                'Closure_particulars': closure_particulars.upper(),
                'Closure_handled_by': closure_handled_by.upper(),
                'Closure_remarks': closure_remarks.upper(),
                'Status': 'Completed'
            }
            result = database.add_further_proc_record(data_dict, r_id)
            try:
                if request.FILES['myfile']:
                    myfile = request.FILES['myfile']
                    now = datetime.now()
                    date_time = now.strftime("%m%d%Y%H%M%S")
                    only_file_name = myfile.name.rsplit('.',1)[0]+date_time
                    file = only_file_name+"."+myfile.name.rsplit('.', 1)[1]
                    file_data = {
                        'File_name': file
                    }
                    file_update = database.add_further_proc_file_record(file_data, r_id)
                    fs = FileSystemStorage()
                    filename = fs.save(file, myfile)
                    uploaded_file_url = fs.url(file)
            except Exception as ex:
                pass
            if close_proceedings == "Yes":
                return judicial_proceedings_landing(request)
            if close_proceedings == 'No':
                proccedingType = exist_result['Type']
                if proccedingType == 1:
                    return regular_proceedings_landing(request)
                if proccedingType == 2:
                    return judicial_proceedings_landing(request)
                if proccedingType == 3:
                    return landing(request)

        if status == 'Completed':
            closure_remarks = request.POST.get('Closure_Remarks')
            data_dict = {
                'Closure_remarks': closure_remarks.upper(),
            }
            data_update = database.update_proc_details(r_id, data_dict)
            proccedingType = exist_result['Type']
            if proccedingType == 1:
                return regular_proceedings_landing(request)
            if proccedingType == 2:
                return judicial_proceedings_landing(request)
            if proccedingType == 3:
                return landing(request)


def submit_proceedings_events(request):
    r_id = request.POST.get('Record_Id')
    event_handled_by = request.POST.get('Event_Handled_By')
    event_type = request.POST.get('Event_type')
    event_Remarks = request.POST.get('Event_Remarks')
    event_particulars = request.POST.get('Event_Particulars')
    event_date = request.POST.get('Event_Date')
    event_actual_date = request.POST.get('Event_Actual_Date')
    event_next_date = request.POST.get('Event_Next_date')

    data_dict = {
        'Proceeding_id': r_id,
        'Event_handled_by': event_handled_by.upper(),
        'Event_type': event_type.upper(),
        'Event_remarks': event_Remarks.upper(),
        'Event_particulars': event_particulars.upper(),
        'Event_date': event_date,
        'Event_actual_date': event_actual_date,
        'Event_next_date': event_next_date,

    }
    result = database.add_event_details(data_dict)
    data_dict = {
        'Closure_date': event_next_date,
        'Closure_particulars': event_particulars.upper(),
        'Closure_remarks': event_Remarks.upper()
    }
    add_date = database.add_further_proc_record(data_dict, r_id)
    data_dict = {
        'Event': 1,
        'Event_actual_date': event_actual_date
    }
    data_update = database.update_proc_details(r_id, data_dict)
    return further_proc_info(request, r_id)

def event_landing(request, id):
    exist_result = database.get_proc_for_event_details(id)
    exist_result['Client_code'] = database.get_client_code_from_name(exist_result['Name'])
    exist_result['Group_name'] = database.get_group_name_from_client_name(exist_result['Name'])

    event_result = database.get_event_details(id)

    return render(request, 'event_landing.html', {'Data_Dict': exist_result, 'Event_list': event_result})

def pdf_view(request, id):
    fs = FileSystemStorage()
    exist_result = database.get_proc_details(id)
    filename = exist_result['File_name']

    if fs.exists(filename):
        with fs.open(filename) as pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            # response['Content-Disposition'] = 'attachment; filename="mypdf.pdf"' #user will be prompted with the browser's open/save file
            response[
                'Content-Disposition'] = 'inline; filename="KARAN03132022015234.pdf"'  # user will be prompted display the PDF in the browser
            return response
    else:
        return HttpResponseNotFound('The requested pdf was not found.')


def delete_proceedings(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        id = request.POST.get('proceedingId')
        if client_database.verify_password("Record Delete", password): 
            if database.delete_proceedings_record(id):
                return JsonResponse({'status': 'success', 'message': 'Record deleted successfully.'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Record not found.'}, status=404)
        else:
            return JsonResponse({'status': 'error', 'message': 'Incorrect password.'}, status=403)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

