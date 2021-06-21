from django.shortcuts import render
from . import database, request_data_retrieve

# Create your views here.


def landing(request):
    ay_list = database.get_ay_list()
    all_client_list = database.get_all_clients_details()
    return render(request, 'landing_reports.html', {'Client_list': all_client_list, 'AY_list': ay_list})


def submit_reports(request):
    status = request.POST.get('Status')
    read_final = 'All'
    if status == "1":
        read_final = 'Yes'
    elif status == "2":
        read_final = 'No'
    task_list = request_data_retrieve.get_selected_tasks(request.POST)
    period_list = request_data_retrieve.get_period(request.POST, task_list)
    group_name_list = request_data_retrieve.get_group_name(request.POST)
    client_name = request.POST.get("Client_Name")
    result_list = []
    for task in task_list:
        if task == 'ROI':
            roi_result = database.get_roi_result(client_name, group_name_list, period_list['ROI'], read_final)
            result_list.extend(roi_result)
        if task == 'Certificates':
            cert_result = database.get_cert_result(client_name, group_name_list, period_list['Certificates'], read_final)
            result_list.extend(cert_result)
        if task == 'otherForms':
            other_result = database.get_other_result(client_name, group_name_list, period_list['OtherForms'], read_final)
            result_list.extend(other_result)
    return render(request, 'report_list.html', {'Result_list': result_list})


def read_unread(request, r_type, r_id):
    type_name = database.get_r_type(r_type)
    if type_name:
        # check if record exists
        record = database.get_record_from_db(r_id, type_name)
        if record:
            return render(request, 'read_unread.html', {'r_type': r_type, 'Record_Data': record})
    return render(request, 'report_list.html')


def read_submit(request):
    r_id = request.POST.get('recordID')
    r_type = request.POST.get('recordType')
    read_check = request.POST.get('read')
    reader = request.POST.get('reader')
    type_name = database.get_r_type(r_type)
    if type_name:
        # check if record exists
        record = database.get_record_from_db(r_id, type_name)
        if record:
            if read_check == 'Yes':
                read_check_final = 'Yes'
            else:
                read_check_final = 'No'

            if reader == 'DHDIWAN':
                reader_final = 'DHDIWAN'
            else:
                reader_final = 'VHDIWAN'
            result = database.submit_read_info(r_id, type_name, read_check_final, reader_final)
            if not result:
                err_message = True
                return render(request, 'read_unread.html', {'r_type': r_type, 'Record_Data': record, 'Error': err_message})
    ay_list = database.get_ay_list()
    all_client_list = database.get_all_clients_details()
    return render(request, 'landing_reports.html', {'Client_list': all_client_list, 'AY_list': ay_list})