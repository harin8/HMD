import ssl

import pymongo as pymongo
from django.shortcuts import render
from IT_Return import database


# Create your views here.

def landing(request):
    return render(request, 'landing.html')


def new_it_return(request):
    ay = request.GET.get('A.Y')
    return_type = request.GET.get('Type')
    ay_list = database.get_ay_list()
    if not ay:
        return render(request, 'it_return.html', {'AY_list': ay_list})
    else:
        return_type_name = database.get_return_type_name_from_id(return_type)
        all_return_list = database.get_all_return_list(ay, return_type_name)
        return render(request, 'it_return.html', {'AY_Selected': ay, 'AY_list': ay_list,
                                                  'Return_Type_Selected': return_type, 'Return_List': all_return_list})


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


def submit_new_return(request):
    ay_list = database.get_ay_list()
    ay = request.POST.get('AY')
    return_type = request.POST.get('type')
    return_type_name = database.get_return_type_name_from_id(return_type)
    return_data_dict = {
        'It_no': request.POST.get('It_No'),
        'Name': request.POST.get('name').upper(),
        'Accepted_by': request.POST.get('acceptedBy').upper(),
        'Acceptance_date': request.POST.get('acceptedDate'),
        'AY': ay,
        'Type': return_type_name,
        'Status': 'Initiated',
        'Submitted_ini': True}
    return_result = database.add_return_record(return_data_dict)
    all_return_list = database.get_all_return_list(ay, return_type_name)
    return render(request, 'it_return.html', {'AY_list': ay_list, 'AY_Selected': ay,
                                              'Return_Type_Selected': return_type,
                                              'Return_List': all_return_list})


def further_return_info(request, it_no, ay, r_type):
    ay_list = database.get_ay_list()
    return_type_name = database.get_return_type_name_from_id(r_type)
    # check if exists in db
    exist_result = database.get_return_details(it_no, ay, return_type_name)
    if exist_result:
        return render(request, 'further_return_info.html', {'AY_Selected': ay, 'AY_list': ay_list,
                                                            'Type': r_type, 'Data_Dict': exist_result,
                                                            'Allow_Further': True})
    return render(request, 'create_new_return.html', {'Name': it_no, 'AY_Selected': ay, 'Type': r_type,
                                                      'AY_list': ay_list})


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
    if all_return_list:
        for data in all_return_list:
            data['Type_id'] = database.get_return_type_id_from_name(data['Type'])

    return render(request, 'existing_return.html', {'Return_List': all_return_list})


def cpc_list(request):
    all_return_list = database.get_cpc_all_return_list()
    if all_return_list:
        for data in all_return_list:
            data['Type_id'] = database.get_return_type_id_from_name(data['Type'])
            data['Due_date'] = database.calculate_due_date_cpc(data['Filing_date'])
    return render(request, 'cpc_list.html', {'CPC_List': all_return_list})


def existing_return_list(request):
    all_return_list = database.get_existing_completed_return_list()
    if all_return_list:
        for data in all_return_list:
            data['Type_id'] = database.get_return_type_id_from_name(data['Type'])
    return render(request, 'existing_return.html', {'Return_List': all_return_list})


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


def further_cpc_submit(request):
    ay = request.POST.get('AY')
    return_type = request.POST.get('type')
    return_type_name = database.get_return_type_name_from_id(return_type)
    return_proof = request.POST.get('verification')
    return_proof_name = database.get_return_proof_name_from_id(return_proof)
    all_return_list = database.get_cpc_all_return_list()
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
    if all_return_list:
        for data in all_return_list:
            data['Type_id'] = database.get_return_type_id_from_name(data['Type'])
            data['Due_date'] = database.calculate_due_date_cpc(data['Filing_date'])
    return render(request, 'cpc_list.html', {'CPC_List': all_return_list})
