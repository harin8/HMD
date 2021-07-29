from django.shortcuts import render
from . import database, request_data_retrieve

# Create your views here.


def landing(request):
    ay_list = database.get_ay_list()
    all_client_list = database.get_all_clients_details()
    party_list = database.get_party_list()
    return render(request, 'landing_reports.html', {'Client_list': all_client_list, 'AY_list': ay_list,
                                                    'Party_list': party_list})


def submit_reports(request):
    status = request.POST.getlist('Status', None)
    if '1' in status and '2' in status:
        read_final = 'All'
    elif '1' in status and '2' not in status:
        read_final = 'Read'
    elif '1' not in status and '2' in status:
        read_final = 'Unread'
    else:
        read_final = 'Read'
    task_list = request_data_retrieve.get_selected_tasks(request.POST)
    if task_list and status:
        period_list = request_data_retrieve.get_period(request.POST, task_list)
        group_name_list = request_data_retrieve.get_group_name(request.POST)
        party_name_list = request_data_retrieve.get_party_name(request.POST)
        client_name = request.POST.getlist("Client_Name")
        result_list = []
        if party_name_list and group_name_list and client_name:
            for task in task_list:
                if task == 'ROI':
                    roi_result = database.get_roi_result(client_name, group_name_list, period_list['ROI'], read_final, party_name_list)
                    result_list.extend(roi_result)
                if task == 'Certificates':
                    cert_result = database.get_cert_result(client_name, group_name_list, period_list['Certificates'], read_final, party_name_list)
                    result_list.extend(cert_result)

                if task == 'Other':
                    other_result = database.get_other_result(client_name, group_name_list, period_list['Other'], read_final, party_name_list)
                    result_list.extend(other_result)

            return render(request, 'report_list.html', {'Result_list': result_list})
    ay_list = database.get_ay_list()
    all_client_list = database.get_all_clients_details()
    party_list = database.get_party_list()
    return render(request, 'landing_reports.html', {'Client_list': all_client_list, 'AY_list': ay_list,
                                                    'Party_list': party_list})


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
    remark = request.POST.get('remark').upper()
    type_name = database.get_r_type(r_type)
    if type_name:
        # check if record exists
        record = database.get_record_from_db(r_id, type_name)
        if record:
            if read_check == 'Read':
                read_check_final = 'Read'
            else:
                read_check_final = 'No'

            if reader == 'DHDIWAN':
                reader_final = 'DHDIWAN'
            else:
                reader_final = 'VHDIWAN'
            result = database.submit_read_info(r_id, type_name, read_check_final, reader_final, remark)
            if not result:
                err_message = True
                return render(request, 'read_unread.html', {'r_type': r_type, 'Record_Data': record, 'Error': err_message})
    ay_list = database.get_ay_list()
    all_client_list = database.get_all_clients_details()
    party_list = database.get_party_list()
    return render(request, 'landing_reports.html', {'Client_list': all_client_list, 'AY_list': ay_list,
                                                    'Party_list': party_list})