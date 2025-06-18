from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from IT_Return import database
from accounts.decorators import permission_required
from proceedings import database as proc_database
import clients.database as client_database

# Create your views here.
@login_required
def landing(request):
    """Updated landing view with marked cases support"""
    show_marked_only = request.GET.get('show_marked_only', 'false').lower() == 'true'
    username = request.user.id if show_marked_only else None
    
    proc_list = proc_database.live_board_proceedings_list(username, show_marked_only)
    
    live_board_unique_proceedings = []
    for data in proc_list:
        data['Client_code'] = proc_database.get_client_code_from_name(data['Name'])
        data['Group_name'] = proc_database.get_group_name_from_client_name(data['Name'])
        live_board_unique_proceedings.append(data['Description'])
    
    return render(request, 'landing.html', {
        'Live_Board': proc_list,
        'Unique_Proceedings': list(set(live_board_unique_proceedings)),
        'show_marked_only': show_marked_only
    })

@login_required
@permission_required('IT_Return', 'view')
def new_it_return(request):
    ay = request.GET.get('A.Y')
    return_type = request.GET.get('Type')
    ay_list = database.get_ay_list()
    if not ay:
        return render(request, 'it_return.html', {'AY_list': ay_list})
    else:
        return_type_name = database.get_return_type_name_from_id(return_type)
        all_return_list = database.get_all_return_list(ay, return_type_name)
        for data in all_return_list:
            data['Client_code'] = database.get_client_code_from_name(data['Name'])
            data['Group_name'] = database.get_group_name_from_client_code(data['Client_code'])
        return render(request, 'it_return.html', {'AY_Selected': ay, 'AY_list': ay_list,
                                                  'Return_Type_Selected': return_type, 'Return_List': all_return_list})


@permission_required('IT_Return', 'add')
def create_new_return(request, it_no, ay, r_type):
    ay_list = database.get_ay_list()
    return_type_name = database.get_return_type_name_from_id(r_type)
    # check if exists in db
    exist_result = database.get_return_details(it_no, ay, return_type_name)
    if exist_result:
        return render(request, 'create_new_return.html', {'It_no': it_no, 'Name': exist_result['Name'],
                                                          'AY_Selected': ay, 'Type': r_type, 'AY_list': ay_list,
                                                          'Data_Dict': exist_result})
    return render(request, 'create_new_return.html', {'It_no': it_no, 'Name': exist_result['Name'],
                                                      'AY_Selected': ay, 'Type': r_type,
                                                      'AY_list': ay_list})


@permission_required('IT_Return', 'add')
def submit_new_return(request):
    ay_list = database.get_ay_list()
    ay = request.POST.get('AY')
    return_type = request.POST.get('type')
    return_type_name = database.get_return_type_name_from_id(return_type)
    acceptance_date = request.POST.get('acceptedDate')
    #acceptance_date_type = database.string_to_date(acceptance_date)
    return_data_dict = {
        'It_no': request.POST.get('It_No'),
        'Name': request.POST.get('name').upper(),
        'Accepted_by': request.POST.get('acceptedBy').upper(),
        'Acceptance_date': acceptance_date,
        'AY': ay,
        'Type': return_type_name,
        'Status': 'Initiated',
        'Submitted_ini': True}
    return_result = database.add_return_record(return_data_dict)
    all_return_list = database.get_all_return_list(ay, return_type_name)
    for data in all_return_list:
        data['Client_code'] = database.get_client_code_from_name(data['Name'])
        data['Group_name'] = database.get_group_name_from_client_code(data['Client_code'])
    return render(request, 'it_return.html', {'AY_list': ay_list, 'AY_Selected': ay,
                                              'Return_Type_Selected': return_type,
                                              'Return_List': all_return_list})


@permission_required('IT_Return', 'view')
def further_return_info(request, it_no, ay, r_type):
    ay_list = database.get_ay_list()
    return_type_name = database.get_return_type_name_from_id(r_type)
    # check if exists in db
    exist_result = database.get_return_details(it_no, ay, return_type_name)
    if exist_result:
        return render(request, 'further_return_info.html', {'AY_Selected': ay, 'AY_list': ay_list,
                                                            'Type': r_type, 'Data_Dict': exist_result,
                                                            'Allow_Further': True})
    return render(request, 'create_new_return.html', {'Name': exist_result['Name'], 'AY_Selected': ay, 'Type': r_type,
                                                      'AY_list': ay_list})


@permission_required('IT_Return', 'add')
def further_return_submit(request):
    ay_list = database.get_ay_list()
    ay = request.POST.get('AY')
    save_bool = request.POST.get('save_fur', True)
    if save_bool == 'false':
        save_bool_final = False
    else:
        save_bool_final = True
    return_type = request.POST.get('type')
    return_type_name = database.get_return_type_name_from_id(return_type)
    return_proof = request.POST.get('verification')
    return_proof_name = database.get_return_proof_name_from_id(return_proof)
    return_data_dict = {'Name': request.POST.get('name').upper(),
                        'It_no': request.POST.get('It_No'),
                        'AY': ay,
                        'Type': return_type_name,
                        'Handled_by': request.POST.get('handledBy').upper(),
                        'Checked_by': request.POST.get('checkedBy').upper(),
                        'Filing_date': request.POST.get('filingDate'),
                        'Remarks': request.POST.get('remarks').upper(),
                        'Verification': return_proof_name,
                        'Ack_no': request.POST.get('acknowledgmentNo'),
                        'Filed_by': request.POST.get('filedBy').upper(),
                        'Submitted_fur': save_bool_final}

    return_result = database.add_further_return_record(return_data_dict)
    all_return_list = database.get_existing_completed_return_list()
    for data in all_return_list:
        data['Client_code'] = database.get_client_code_from_name(data['Name'])
        data['Group_name'] = database.get_group_name_from_client_code(data['Client_code'])
    if all_return_list:
        for data in all_return_list:
            data['Type_id'] = database.get_return_type_id_from_name(data['Type'])

    return render(request, 'existing_return.html', {'Return_List': all_return_list})


@permission_required('IT_Return', 'view')
def cpc_list(request):
    all_return_list = database.get_cpc_all_return_list()

    if all_return_list:
        for data in all_return_list:
            data['Type_id'] = database.get_return_type_id_from_name(data['Type'])
            data['Due_date'] = database.calculate_due_date_cpc(data['Filing_date'])
            try:
                data['Acceptance_date'] = database.ymd_str_to_IST_format(data['Acceptance_date'])
            except Exception:
                pass
            try:
                data['Filing_date'] = database.ymd_str_to_IST_format(data['Filing_date'])
            except Exception:
                pass
            data['Group_name'] = database.get_group_name_from_client_code(data['Client_code'])
    return render(request, 'cpc_list.html', {'CPC_List': all_return_list})


@permission_required('IT_Return', 'view')
def existing_return_list(request):
    all_return_list = database.get_existing_completed_return_list()
    if all_return_list:
        for data in all_return_list:
            try:
                data['Acceptance_date'] = database.ymd_str_to_IST_format(data['Acceptance_date'])
            except Exception:
                pass
            try:
                data['Filing_date'] = database.ymd_str_to_IST_format(data['Filing_date'])
            except Exception:
                pass
            data['Type_id'] = database.get_return_type_id_from_name(data['Type'])
            data['Group_name'] = database.get_group_name_from_client_name(data['Name'])
    return render(request, 'existing_return.html', {'Return_List': all_return_list})


@permission_required('IT_Return', 'add')
def further_cpc_info(request, it_no, ay, r_type):
    ay_list = database.get_ay_list()
    # check if exists in db
    r_type_name = database.get_return_type_name_from_id(r_type)
    exist_result = database.get_return_details(it_no, ay, r_type_name)
    exist_result = database.get_client_code_from_result(exist_result)
    if exist_result:
        exist_result['Due_date'] = database.calculate_due_date_cpc(exist_result['Filing_date'])
        return render(request, 'further_cpc_info.html', {'Name': it_no, 'AY_Selected': ay, 'Type': r_type,
                                                         'AY_list': ay_list,
                                                         'Data_Dict': exist_result, 'Allow_Further': True})
    return render(request, 'create_cpc_return.html', {'Name': it_no, 'AY_Selected': ay, 'Type': r_type,
                                                      'AY_list': ay_list})


@permission_required('IT_Return', 'add')
def further_cpc_submit(request):
    ay = request.POST.get('AY')
    return_type = request.POST.get('type')
    return_type_name = database.get_return_type_name_from_id(return_type)
    return_proof = request.POST.get('verification')
    return_proof_name = database.get_return_proof_name_from_id(return_proof)
    if ay and return_type and return_proof:
        return_data_dict = {'Name': request.POST.get('clientName').upper(),
                            'AY': ay,
                            'Type': return_type_name,
                            'Remarks_cpc': request.POST.get('remarksCPC').upper(),
                            'Completed_by': request.POST.get('completedBy').upper(),
                            'Completed_on': request.POST.get('completedOn'),
                            'Due_date': request.POST.get('dueDate_CPC'),
                            'Verification': return_proof_name}

        return_result = database.add_cpc_return_record(return_data_dict)
    all_return_list = database.get_cpc_all_return_list()
    if all_return_list:
        for data in all_return_list:
            data['Client_code'] = database.get_client_code_from_name(data['Name'])
            data['Group_name'] = database.get_group_name_from_client_code(data['Client_code'])
            data['Type_id'] = database.get_return_type_id_from_name(data['Type'])
            data['Due_date'] = database.calculate_due_date_cpc(data['Filing_date'])
    return render(request, 'cpc_list.html', {'CPC_List': all_return_list})


def group_filter_list(request):
    """Get list of groups for filtering"""
    try:
        group_list = database.get_all_available_group_code()
        if group_list:
            return JsonResponse(group_list[0], safe=False)
        return JsonResponse({})
    except Exception as e:
        print(f"Error fetching group list: {str(e)}")
        return JsonResponse({'error': 'Failed to fetch groups'}, status=500)


@permission_required('IT_Return', 'delete')
def delete_return(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        it_no = request.POST.get('returnITCode')
        ay = request.POST.get('returnAY')
        r_type = request.POST.get('returnType')
        return_type_name = database.get_return_type_name_from_id(r_type)
        if client_database.verify_password("Record Delete", password):  # Replace with your actual password check
            if database.delete_it_return(it_no, ay, return_type_name):
                return JsonResponse({'status': 'success', 'message': 'Record deleted successfully.'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Record not found.'}, status=404)
        else:
            return JsonResponse({'status': 'error', 'message': 'Incorrect password.'}, status=403)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)
