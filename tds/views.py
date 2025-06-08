from django.shortcuts import render
from . import database
import clients.database as client_database
from django.http import JsonResponse

# Create your views here.


def tds_landing(request):
    ay = request.GET.get('A.Y')
    quarter = request.GET.get('tdsQuarter')
    form = request.GET.get('tdsForm')
    type = request.GET.get('tdsType')
    ay_list = database.get_ay_list()
    tds_form_list = database.get_tds_form_list()
    tds_type_list = database.get_tds_type_list()
    tds_quarter_list = database.get_tds_quarter_list()
    if ay:
        form_name = database.get_tds_form_name_from_id(form)
        type_name = database.get_tds_type_name_from_id(type)
        quarter_name = database.get_tds_quarter_name_from_id(quarter)
        all_tds_list = database.get_all_tds_list(ay, type_name, form_name, quarter_name)
        for data in all_tds_list:
            data['Form_id'] = database.get_tds_form_id_from_name(form_name)
            data['Type_id'] = database.get_tds_type_id_from_name(type_name)
            data['Quarter_id'] = database.get_tds_quarter_id_from_name(quarter_name)
            data['Group_name'] = database.get_group_name_from_client_code(data['Client_code'])
            try:
                data['Acceptance_date'] = database.ymd_str_to_IST_format(data['Acceptance_date'])
            except Exception:
                pass

        return render(request, 'tds_landing.html', {'AY_List': ay_list, 'TDS_Form': tds_form_list,
                                                    'TDS_Type': tds_type_list, 'All_TDS_List': all_tds_list,
                                                    'TDS_Quarter': tds_quarter_list})
    else:
        return render(request, 'tds_landing.html', {'AY_List': ay_list, 'TDS_Form': tds_form_list,
                                                    'TDS_Type': tds_type_list, 'TDS_Quarter': tds_quarter_list})


def create_new_tds(request, client_no, ay, quarter, form, type):
    quarter_name = database.get_tds_quarter_name_from_id(quarter)
    form_name = database.get_tds_form_name_from_id(form)
    type_name = database.get_tds_type_name_from_id(type)
    # check if exists in db
    exist_tds = database.get_tds_details(client_no, ay, quarter_name, form_name, type_name)
    if exist_tds:
        exist_tds['AY'] = ay
        exist_tds['Quarter'] = quarter_name
        exist_tds['Form'] = form_name
        exist_tds['Type'] = type_name
        return render(request, 'create_new_tds.html', {'Client_code': client_no, 'Data_Dict': exist_tds})
    ay_list = database.get_ay_list()
    tds_form_list = database.get_tds_form_list()
    tds_type_list = database.get_tds_type_list()
    tds_quarter_list = database.get_tds_quarter_list()
    return render(request, 'tds_landing.html', {'AY_List': ay_list, 'TDS_Form': tds_form_list,
                                                'TDS_Type': tds_type_list, 'TDS_Quarter': tds_quarter_list})


def submit_new_tds(request):
    client_no = request.POST.get('clientNo')
    ay = request.POST.get('tdsAY')
    quarter = request.POST.get('tdsQuarter')
    form = request.POST.get('tdsForm')
    tds_type = request.POST.get('tdsType')
    name = database.get_client_name_from_client_code(client_no)
    if name:
        return_data_dict = {
            'Client_code': client_no,
            'Name': name,
            'Accepted_by': request.POST.get('acceptedBy').upper(),
            'Acceptance_date': request.POST.get('acceptedDate'),
            'AY': ay,
            'Quarter': quarter,
            'Form': form,
            'Type': tds_type,
            'Status': 'Initiated',
            'Submitted_ini': True}
        return_result = database.add_tds_record(return_data_dict)

        ay_list = database.get_ay_list()
        tds_form_list = database.get_tds_form_list()
        tds_type_list = database.get_tds_type_list()
        tds_quarter_list = database.get_tds_quarter_list()
        all_tds_list = database.get_all_tds_list(ay, tds_type, form, quarter)
        for data in all_tds_list:
            data['Form_id'] = database.get_tds_form_id_from_name(form)
            data['Type_id'] = database.get_tds_type_id_from_name(tds_type)
            data['Quarter_id'] = database.get_tds_quarter_id_from_name(quarter)
            data['Client_code'] = database.get_client_code_from_name(data['Name'])
            data['Group_name'] = database.get_group_name_from_client_code(data['Client_code'])

        return render(request, 'tds_landing.html', {'AY_List': ay_list, 'TDS_Form': tds_form_list,
                                                    'TDS_Type': tds_type_list, 'TDS_Quarter': tds_quarter_list,
                                                    'All_TDS_List': all_tds_list})


def existing_tds_list(request):
    all_tds_list = database.get_existing_completed_tds_list()
    if all_tds_list:
        for data in all_tds_list:
            data['Form_id'] = database.get_tds_form_id_from_name(data['Form'])
            data['Type_id'] = database.get_tds_type_id_from_name(data['Type'])
            data['Quarter_id'] = database.get_tds_quarter_id_from_name(data['Quarter'])
            data['Group_name'] = database.get_group_name_from_client_code(data['Client_code'])
    return render(request, 'existing_tds.html', {'TDS_List': all_tds_list})


def further_tds_info(request, client_no, ay, quarter, form, type):
    quarter_name = database.get_tds_quarter_name_from_id(quarter)
    form_name = database.get_tds_form_name_from_id(form)
    type_name = database.get_tds_type_name_from_id(type)
    # check if exists in db
    exist_tds = database.get_tds_details(client_no, ay, quarter_name, form_name, type_name)
    if exist_tds:
        exist_tds['AY'] = ay
        exist_tds['Quarter'] = quarter_name
        exist_tds['Form'] = form_name
        exist_tds['Type'] = type_name
        return render(request, 'further_tds_info.html', {'Data_Dict': exist_tds, 'Allow_Further': True})
    return render(request, 'create_new_tds.html', {'Client_code': client_no, 'Data_Dict': exist_tds})


def further_tds_submit(request):
    ay = request.POST.get('tdsAY')
    save_bool = request.POST.get('save_fur', True)
    if save_bool == 'false':
        save_bool_final = False
    else:
        save_bool_final = True
    tds_type = request.POST.get('tdsType')
    tds_quarter = request.POST.get('tdsQuarter')
    tds_form = request.POST.get('tdsForm')
    filing_mode = request.POST.get('filingMode')
    filing_mode_name = database.get_tds_filing_mode_name_from_id(filing_mode)
    return_data_dict = {'Name': request.POST.get('name').upper(),
                        'Client_code': request.POST.get('clientCode'),
                        'AY': ay,
                        'Quarter': tds_quarter,
                        'Form': tds_form,
                        'Type': tds_type,
                        'Handled_by': request.POST.get('handledBy').upper(),
                        'Checked_by': request.POST.get('checkedBy').upper(),
                        'Filing_date': request.POST.get('filingDate'),
                        'Remarks': request.POST.get('remarks').upper(),
                        'Filing_mode': filing_mode_name,
                        'Token_no': request.POST.get('tokenNo'),
                        'Filed_by': request.POST.get('filedBy').upper(),
                        'Submitted_fur': save_bool_final}

    return_result = database.add_further_tds_record(return_data_dict)
    all_tds_list = database.get_existing_completed_tds_list()
    for data in all_tds_list:
        data['Form_id'] = database.get_tds_form_id_from_name(data['Form'])
        data['Type_id'] = database.get_tds_type_id_from_name(data['Type'])
        data['Quarter_id'] = database.get_tds_quarter_id_from_name(data['Quarter'])
        data['Group_name'] = database.get_group_name_from_client_code(data['Client_code'])

    return render(request, 'existing_tds.html', {'TDS_List': all_tds_list})


def delete_tds(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        client_code = request.POST.get('tdsClientCode')
        ay = request.POST.get('tdsAY')
        quarter_id = request.POST.get('tdsQuarterId')
        quarter_id_name = database.get_tds_quarter_name_from_id(quarter_id)
        form_id = request.POST.get('tdsFormId')
        form_id_name = database.get_tds_form_name_from_id(form_id)
        type_id = request.POST.get('tdsTypeId')
        type_id_name = database.get_tds_type_name_from_id(type_id)
        if client_database.verify_password("Record Delete", password):  # Replace with your actual password check
            if database.delete_tds_return(client_code, ay, quarter_id_name, form_id_name, type_id_name):
                return JsonResponse({'status': 'success', 'message': 'Record deleted successfully.'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Record not found.'}, status=404)
        else:
            return JsonResponse({'status': 'error', 'message': 'Incorrect password.'}, status=403)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)