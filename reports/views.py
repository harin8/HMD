from django.shortcuts import render
from . import database, request_data_retrieve
from accounts.decorators import permission_required

# Create your views here.
@permission_required('reports', 'view')
def landing(request):
    ay_list = database.get_ay_list()
    all_client_list = database.get_all_clients_details()
    party_list = database.get_party_list()
    return render(request, 'landing_reports.html', {'Client_list': all_client_list, 'AY_list': ay_list,
                                                    'TDS_list': ay_list, 'Party_list': party_list,
                                                    'Proceedings_list': ay_list})


@permission_required('reports', 'add')
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
                    roi_result = database.get_roi_result(client_name, group_name_list, period_list['ROI'], read_final,
                                                         party_name_list)
                    result_list.extend(roi_result)
                if task == 'Certificates':
                    cert_result = database.get_cert_result(client_name, group_name_list, period_list['Certificates'],
                                                           read_final, party_name_list)
                    result_list.extend(cert_result)
                if task == 'Other':
                    other_result = database.get_other_result(client_name, group_name_list, period_list['Other'],
                                                             read_final, party_name_list)
                    result_list.extend(other_result)
                if task == 'TDS':
                    tds_result = database.get_tds_result(client_name, group_name_list, period_list['TDS'], read_final,
                                                         party_name_list)
                    result_list.extend(tds_result)
                if task == 'Proceedings':
                    proceedings_result = database.get_proceedings_result(client_name, group_name_list,
                                                                         period_list['Proceedings'], read_final,
                                                                         party_name_list)
                    result_list.extend(proceedings_result)
            
            if request.POST.get('report_type') == 'cost_sheet':
                return render(request, 'report_list_new_cost_sheet.html',  {'Result_list': result_list})
            else:
                return render(request, 'report_list_new.html', {'Result_list': result_list})

    ay_list = database.get_ay_list()
    all_client_list = database.get_all_clients_details()
    party_list = database.get_party_list()
    
    return render(request, 'landing_reports.html', {'Client_list': all_client_list, 'AY_list': ay_list,
                                                    'TDS_list': ay_list, 'Party_list': party_list,
                                                    'Proceedings_list': ay_list})


@permission_required('reports', 'view')
def read_unread(request, r_type, r_id):
    type_name = database.get_r_type(r_type)
    if type_name:
        # check if record exists
        record = database.get_record_from_db(r_id, type_name)
        if record:
            return render(request, 'read_unread.html', {'r_type': r_type, 'Record_Data': record})
    ay_list = database.get_ay_list()
    all_client_list = database.get_all_clients_details()
    party_list = database.get_party_list()
    return render(request, 'landing_reports.html', {'Client_list': all_client_list, 'AY_list': ay_list,
                                                    'TDS_list': ay_list, 'Party_list': party_list,
                                                    'Proceedings_list': ay_list})


'''def read_submit(request):
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
                                                    'TDS_list': ay_list, 'Party_list': party_list,
                                                    'Proceedings_list': ay_list})'''


@permission_required('reports', 'add')
def read_submit(request):
    r_id = request.POST.getlist('r_id')
    remark = request.POST.getlist('remark')
    all_type = request.POST.getlist('task')
    password = request.POST.get('password')
    if not database.verify_password("Report Read Submit", password):
        all_records = []
        for x in range(len(r_id)):
            type_name = database.get_r_type(all_type[x])
            if type_name:
                # check if record exists
                record = database.get_record_from_db(r_id[x], type_name)
                record['Party_name'] = database.get_party_name_from_name(record['Name'])
                record['Client_code'] = database.get_client_code_from_name(record['Name'])
                if record:
                    all_records.append(record)
        return render(request, 'read_unread_new.html', {'All_Records': all_records})
    else:
        # check if record exists
        for x in range(len(r_id)):
            type_name = database.get_r_type(all_type[x])
            remark_new = remark[x].upper()
            result = database.submit_read_info(r_id[x], type_name, 'Read', remark_new)
        ay_list = database.get_ay_list()
        all_client_list = database.get_all_clients_details()
        party_list = database.get_party_list()
        return render(request, 'landing_reports.html', {'Client_list': all_client_list, 'AY_list': ay_list,
                                                        'TDS_list': ay_list, 'Party_list': party_list,
                                                        'Proceedings_list': ay_list})


@permission_required('reports', 'add')
def client_reports_submit(request):
    all_id = request.POST.getlist('ids')
    all_types = request.POST.getlist('types')
    all_records = []
    for x in all_id:
        r_id = x.split(',')
    for x in all_types:
        r_type = x.split('^,^')
    for x, y in zip(r_id, r_type):
        type_name = database.get_r_type_2(y)
        if type_name:
            # check if record exists
            record = database.get_record_from_db(x, type_name)
            record['Party_name'] = database.get_party_name_from_name(record['Name'])
            record['Client_code'] = database.get_client_code_from_name(record['Name'])
            record['Type_name_hidden'] = type_name
            record['Type_name'] = y
            if record:
                all_records.append(record)
    return render(request, 'read_unread_new.html', {'r_type': r_type, 'All_Records': all_records})
