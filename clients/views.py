from django.http import JsonResponse
from django.shortcuts import render
from clients import database
from contacts import database as contact_database


# Create your views here.

def client_landing(request):
    return render(request, 'client_landing.html')


def client_master_list(request):
    all_return_list = database.get_client_master_list(id_field=False)
    return render(request, 'client_master.html', {'client_List': all_return_list})


def create_new_client(request):
    group_no = request.GET.get('GroupNameForm')
    client_type_form = request.GET.get('ClientTypeForm')

    group_code_name = database.get_all_group_code_name()

    if group_no and client_type_form:
        group_name = database.get_group_name_from_id(group_no)
        client_type_form_name = database.get_client_type_name_from_id(client_type_form)
        show_further = True
        it_no_list = database.get_all_distinct_value('It_no')
        audit_no_list = database.get_all_distinct_value('Audit_no')
        it_start, it_end = database.get_it_no_range(group_name, client_type_form_name)
        audit_start, audit_end = database.get_audit_no_range(group_name, client_type_form_name)
        party_list = database.get_party_list_from_group_name(group_name)
        if (it_start == 0 and it_end == 0) or (audit_start == 0 and audit_end == 0):
            return render(request, 'new_client.html')
        else:
            # convert it no from clientMaster to int
            it_no_list_int = [int(x) for x in it_no_list]
            audit_no_list_int = [int(x) for x in audit_no_list]
            it_no_range = [x for x in range(it_start, it_end + 1)]
            audit_no_range = [x for x in range(audit_start, audit_end + 1)]
            available_it_no = sorted(list(set(it_no_range) - set(it_no_list_int)))
            available_audit_no = sorted(list(set(audit_no_range) - set(audit_no_list_int)))
            contact_list = contact_database.get_all_contact_details(False)
            return render(request, 'new_client.html', {'Show_Further': show_further,
                                                       'Available_It_No': available_it_no,
                                                       'Available_Audit_No': available_audit_no,
                                                       'Group_No': group_no,
                                                       'Type_Selected': client_type_form,
                                                       'Contact_List': contact_list,
                                                       'Party_List': party_list,
                                                       'Group_c_n': group_code_name})

    return render(request, 'new_client.html', {'Group_c_n': group_code_name})


def submit_new_client(request):
    client_name = request.POST.get('name')
    group_name = request.POST.get('groupName', '')
    client_type = request.POST.get('clientType', '')
    party_name = request.POST.get('partyName', '')
    it_no = request.POST.get('itNo', '0')
    it_note = request.POST.get('itNote', '')
    audit_note = request.POST.get('auditNote', '')
    audit_no = request.POST.get('auditNo', '0')
    it_size = request.POST.get('itSize', '0')
    audit_size = request.POST.get('auditSize', '0')
    tds = request.POST.get('TDS', 'no')
    tds_bool = 'True'
    if tds == 'no':
        tds_bool = 'False'
    contact_list = []
    contact_names = request.POST.getlist('contactName')
    contact_designation = request.POST.getlist('contactDesignation')
    it_size_name = database.get_it_audit_size(it_size)
    audit_size_name = database.get_it_audit_size(audit_size)
    error_message = ''
    '''contact_nos = request.POST.getlist('contactNo')
    contact_emails = request.POST.getlist('contactEmail')'''
    if client_type != '' and group_name != '' and party_name != '':
        # check if it_code is already taken or not
        it_code_present = database.check_it_code_present(it_no)
        # check if client name already exists
        client_name_exist = database.check_client_name_present(client_name.upper())
        if not client_name_exist:
            if not it_code_present:
                for x in range(len(contact_names)):
                    # check if contact exists. if yes get mobile no and email from db
                    contact_db = contact_database.get_contact_phone_email_from_name(contact_names[x].upper())
                    if contact_db:
                        temp = {'r_id': contact_db['_id'],
                                'Name': contact_db['Name'], 'Designation': contact_designation[x].upper(),
                                'Contact_no': contact_db['Contact_no'], 'Email': contact_db['Email'],
                                'Remarks': contact_db['Remarks']}
                        contact_list.append(temp)

                data_dict = {'Name': client_name.upper(),
                             'Group_name': group_name.upper(),
                             'Client_type': client_type.upper(),
                             'Party_name': party_name.upper(),
                             'Client_code': it_no,
                             'It_no': it_no,
                             'It_size': it_size_name,
                             'It_note': it_note,
                             'Audit_no': audit_no,
                             'Audit_size': audit_size_name,
                             'Audit_note': audit_note,
                             'TDS': tds_bool,
                             'Contact_details': contact_list
                             }
                data_add = database.add_client_details(data_dict)
        else:
            error_message = 'Client name already exists. Please user different name.'
    all_return_list = database.get_client_master_list(id_field=False)
    return render(request, 'client_master.html', {'client_List': all_return_list, 'error_message': error_message})


def edit_client_list(request):
    all_return_list = database.get_client_master_list(id_field=True)
    return render(request, 'client_master.html', {'client_List': all_return_list,
                                                  'can_edit': True})


def closure_client_list(request):
    all_return_list = database.get_client_master_list(id_field=True)
    closed_client_list = database.get_closed_client_master_list(id_field=False)
    return render(request, 'client_closure_list.html', {'client_List': all_return_list,
                                                        'closed_client_list': closed_client_list, 'can_edit': True})


def edit_one_client(request, id):
    client_details = database.get_client_detail_from_id(id)
    audit_no_list = database.get_all_distinct_value('Audit_no')
    audit_start, audit_end = database.get_audit_no_range(client_details['Group_name'], client_details['Client_type'])
    party_list = database.get_party_list_from_group_name(client_details['Group_name'])

    audit_no_list_int = [int(x) for x in audit_no_list]
    audit_no_range = [x for x in range(audit_start, audit_end + 1)]
    available_audit_no = sorted(list(set(audit_no_range) - set(audit_no_list_int)))
    available_audit_no.append(client_details['Audit_no'])

    contact_list = contact_database.get_all_contact_details(False)

    return render(request, 'edit_client.html', {'Password': True,
                                                'Client_Details': client_details,
                                                'Available_Audit_No': available_audit_no,
                                                'Party_List': party_list,
                                                'Contact_List': contact_list})


def submit_edit_client(request):
    password = request.POST.get('password', '')
    client_id = request.POST.get('clientID')
    party_name = request.POST.get('partyName')
    it_size = request.POST.get('itSize')
    it_size_name = database.get_it_audit_size(it_size)
    it_note = request.POST.get('itNote')
    audit_no = request.POST.get('auditNo')
    audit_size = request.POST.get('auditSize')
    audit_size_name = database.get_it_audit_size(audit_size)
    audit_note = request.POST.get('auditNote')
    tds = request.POST.get('TDS', 'no')
    tds_bool = 'True'
    if tds == 'no':
        tds_bool = 'False'

    contact_list = []
    contact_names = request.POST.getlist('contactName')
    contact_designation = request.POST.getlist('contactDesignation')
    if database.verify_password("Client Edit", password):
        for x in range(len(contact_names)):
            # check if contact exists. if yes get mobile no and email from db
            contact_db = contact_database.get_contact_phone_email_from_name(contact_names[x].upper())
            if contact_db:
                temp = {'r_id': contact_db['_id'],
                        'Name': contact_db['Name'], 'Designation': contact_designation[x].upper(),
                        'Contact_no': contact_db['Contact_no'], 'Email': contact_db['Email'],
                        'Remarks': contact_db['Remarks']}
                contact_list.append(temp)
            else:
                continue

        data_dict = {
            'Party_name': party_name.upper(),
            'It_size': it_size_name,
            'It_note': it_note,
            'Audit_no': audit_no,
            'Audit_size': audit_size_name,
            'Audit_note': audit_note,
            'TDS': tds_bool,
            'Contact_details': contact_list
        }
        update_client = database.update_client_details_edit(client_id, data_dict)
        all_return_list = database.get_client_master_list(id_field=True)
        return render(request, 'client_master.html', {'client_List': all_return_list,
                                                      'can_edit': True})
    else:
        client_details = database.get_client_detail_from_id(client_id)
        audit_no_list = database.get_all_distinct_value('Audit_no')
        audit_start, audit_end = database.get_audit_no_range(client_details['Group_name'],
                                                             client_details['Client_type'])
        party_list = database.get_party_list_from_group_name(client_details['Group_name'])

        audit_no_list_int = [int(x) for x in audit_no_list]
        audit_no_range = [x for x in range(audit_start, audit_end + 1)]
        available_audit_no = sorted(list(set(audit_no_range) - set(audit_no_list_int)))
        available_audit_no.append(client_details['Audit_no'])

        contact_list = contact_database.get_all_contact_details(False)
        return render(request, 'edit_client.html', {'Password': True,
                                                    'Client_Details': client_details,
                                                    'Available_Audit_No': available_audit_no,
                                                    'Party_List': party_list,
                                                    'Contact_List': contact_list,
                                                    'Error': True, 'Alert': "Password is Incorrect."})


def edit_contact(request, id):
    contact_detail = contact_database.get_contact_detail_from_id(id)
    if contact_detail:
        return render(request, 'create_new_contact.html', {'Hide': True, 'Contact_Details': contact_detail})


def party_master_list(request):
    party_size = database.get_client_it_size_list()

    return render(request, 'party_master.html', {'Party_Size': party_size})


def create_new_party(request):
    group_code_name = database.get_all_group_code_name()

    closed_group = database.get_closed_group_list()

    if closed_group and group_code_name:
        for x in closed_group:
            for y, z in group_code_name.items():
                if x['Group'] == z:
                    del group_code_name[y]
                    break
    return render(request, 'new_party.html', {'Group_c_n': group_code_name})


def submit_new_party(request):
    group_no = request.POST.get('GroupNameForm', '')
    party_name = request.POST.get('partyName', '')
    group_name = database.get_group_name_from_id(group_no)
    password = request.POST.get("password", '')

    error_message = "Successful"
    if database.verify_password("Party Creation", password):
        if group_no != '' and party_name != '':
            data_dict = {'Group_name': group_name.upper(),
                         'Party_name': party_name.upper(),
                         }
            data_add = database.add_party_details(data_dict)
            if data_add:
                party_size = database.get_client_it_size_list()
                return render(request, 'party_master.html', {'Party_Size': party_size})
            else:
                error_message = "Error! Party name already exists!"
        else:
            error_message = "Error! Party name or Group name is left empty!"
    else:
        error_message = "Error! Please check the password!"

    group_code_name = database.get_all_group_code_name()
    return render(request, 'new_party.html', {'Alert': error_message, 'Group_c_n': group_code_name})


def close_party_list(request):
    party_list = database.get_party_master_list(id_field=True)
    # Count no of clients in each party
    for x in party_list:
        x['Total_clients'] = database.get_total_client_from_party_name(x['Party_name'])

    return render(request, 'party_master.html', {'can_edit': True, 'Party_List': party_list})


def close_party(request, id):
    party_detail = database.get_party_detail_from_id(id)
    if party_detail:
        group_code = database.get_group_code_from_group_name(party_detail['Group_name'])
        return render(request, 'new_party.html', {'Hide': True, 'G_Code': group_code,
                                                  'Party_Details': party_detail})

    return render(request, 'new_party.html')


def submit_close_party(request):
    r_id = request.POST.get('r_id')
    group_no = request.POST.get('GroupNameForm', '')
    party_name = request.POST.get('partyName', '')
    password = request.POST.get("password")
    group_name = database.get_group_name_from_id(group_no)
    party_detail = database.get_party_detail_from_id(r_id)
    group_code = database.get_group_code_from_group_name(party_detail['Group_name'])
    if database.verify_password("Party Closure", password):
        if group_no != '' and party_name != '':
            data_dict = {'Group_name': group_name.upper(),
                         'Party_name': party_name.upper(),
                         }
            data_update = database.close_party(r_id, data_dict)
            party_list = database.get_party_master_list(id_field=True)
            for x in party_list:
                x['Total_clients'] = database.get_total_client_from_party_name(x['Party_name'])
            return render(request, 'party_master.html', {'can_edit': True, 'Party_List': party_list})
    return render(request, 'new_party.html', {'Error': True, 'Alert': "Could not perform the operation",
                                              'Hide': True, 'Party_Details': party_detail,
                                              'G_Code': group_code})


def transfer_party_list(request):
    party_list = database.get_party_master_list(id_field=True)
    # Count no of clients in each party
    for x in party_list:
        x['Total_clients'] = database.get_total_client_from_party_name(x['Party_name'])

    return render(request, 'party_master.html', {'Transfer': True, 'can_edit': True, 'Party_List': party_list})


def transfer_party(request, id):
    party_detail = database.get_party_detail_from_id(id)
    group_code_name = database.get_all_group_code_name()

    if party_detail:
        client_list = database.get_all_distinct_clients_from_party_name(party_detail['Party_name'])
        return render(request, 'new_party_transfer.html', {'Group_c_n': group_code_name,
                                                           'Party_Detail': party_detail,
                                                           'Client_List': client_list})

    party_list = database.get_party_master_list(id_field=True)
    # Count no of clients in each party
    for x in party_list:
        x['Total_clients'] = database.get_total_client_from_party_name(x['Party_name'])
    return render(request, 'party_master.html', {'Transfer': True, 'can_edit': True, 'Party_List': party_list})


def submit_transfer_party(request):
    r_id = request.POST.get('r_id')
    group_no = request.POST.get('GroupNameForm', '')
    party_name = request.POST.get('partyName', '')
    password = request.POST.get("password")
    group_name = database.get_group_name_from_id(group_no)

    client_ids = request.POST.getlist('client_id')  # Assuming 'client_id' is an array of client IDs
    old_it_nos = request.POST.getlist('oldITNo')

    it_nos = request.POST.getlist('newITNo')

    audit_nos = request.POST.getlist('newAuditCode')

    it_sizes = request.POST.getlist('newITSize')

    audit_sizes = request.POST.getlist('newAuditSize')

    if database.verify_password("Party Transfer", password):
        if group_name and party_name:

            final_update_list = []

            for i, client_id in enumerate(client_ids):
                party_name = party_name
                it_no = it_nos[i] if i < len(it_nos) else ''
                audit_no = audit_nos[i] if i < len(audit_nos) else ''
                it_size = it_sizes[i] if i < len(it_sizes) else ''
                audit_size = audit_sizes[i] if i < len(audit_sizes) else ''
                old_it_no = old_it_nos[i] if i < len(old_it_nos) else ''

                if client_id and (party_name or it_no or audit_no or it_size or audit_size):
                    # check if the new IT code is already taken or not
                    updated_data_dict = {}
                    if party_name:
                        updated_data_dict['Group_name'] = group_name
                    if it_no:
                        updated_data_dict['It_no'] = it_no
                    if audit_no:
                        updated_data_dict['Audit_no'] = audit_no
                    if it_size:
                        updated_data_dict['It_size'] = database.get_it_audit_size(it_size)
                    if audit_size:
                        updated_data_dict['Audit_size'] = database.get_it_audit_size(audit_size)
                    updated_data_dict['Client_code'] = it_no
                    updated_data_dict['OldITNo'] = old_it_no
                    updated_data_dict['Client_id'] = client_id

                    final_update_list.append(updated_data_dict)
                else:
                    group_code_name = database.get_all_group_code_name()
                    party_detail = database.get_party_detail_from_id(r_id)
                    client_list = database.get_all_distinct_clients_from_party_name(party_detail['Party_name'])
                    return render(request, 'new_party_transfer.html',
                                  {'Error': True, 'Alert': "Error while updating the database",
                                   'Hide': True, 'Party_Detail': party_detail,
                                   'Group_c_n': group_code_name,
                                   'Client_List': client_list})
            # Update the client and party details in the database
            if final_update_list:
                # Update party name for the specified group name in partyMaster table
                database.update_party_name_in_party_master(group_name, party_name.upper())
                database.update_client_details(final_update_list)
                party_list = database.get_party_master_list(id_field=True)
                # Count no of clients in each party
                for x in party_list:
                    x['Total_clients'] = database.get_total_client_from_party_name(x['Party_name'])

                return render(request, 'party_master.html',
                              {'Transfer': True, 'can_edit': True, 'Party_List': party_list})

        group_code_name = database.get_all_group_code_name()
        party_detail = database.get_party_detail_from_id(r_id)
        client_list = database.get_all_distinct_clients_from_party_name(party_detail['Party_name'])
        return render(request, 'new_party_transfer.html', {'Error': True, 'Alert': "Password is Incorrect",
                                                           'Hide': True, 'Party_Detail': party_detail,
                                                           'Group_c_n': group_code_name, 'Client_List': client_list})


def group_master_list(request):
    all_group_list = database.get_all_group_list()
    return render(request, 'group_master.html', {"Group_list": all_group_list})


def create_new_group(request):
    available_group_range = database.get_all_available_group_no()

    return render(request, 'new_group.html', {'Group_range': available_group_range})


def submit_new_group(request):
    group_range = request.POST.get('GroupRangeForm', '')
    group_name = request.POST.get('groupName', '').upper()
    heads_name = request.POST.get('headsName', '').upper()
    password = request.POST.get("password", '')
    if database.verify_password("Group Creation", password):
        # check if already exists
        existing_group_names = database.get_all_distinct_group_names()

        if group_name in existing_group_names:
            return render(request, 'new_group.html', {"Alert": "Group Name already exists!!"})

        available_group_range = database.get_all_available_group_no()
        available_group_code = database.get_all_available_group_code()
        group_code = len(available_group_code[0])

        if group_range != "" and group_name != "" and int(group_range) in available_group_range:
            database.insert_group_code_to_db_new(str(group_code), group_name)
            database.insert_new_group_to_db(group_name, group_range, heads_name)
            all_group_list = database.get_all_group_list()
            return render(request, 'group_master.html', {"Group_list": all_group_list})
        else:
            return render(request, 'new_group.html', {"Alert": "Error! Please check the details!",
                                                      'Group_range': available_group_range})
    else:
        available_group_range = database.get_all_available_group_no()
        return render(request, 'new_group.html', {"Alert": "Error! Please check the password!",
                                                  'Group_range': available_group_range})


def close_group_list(request):
    empty_group_list = database.get_empty_group_list()
    closed_group_list = database.get_closed_group_list()
    return render(request, 'close_group_list.html', {"Empty_group_list": empty_group_list,
                                                     "Closed_group_list": closed_group_list})


def close_one_group(request):
    group_name = request.POST.get('groupCloseName', '')
    close_reason = request.POST.get('closeReason', '').upper()
    password = request.POST.get("password", '')

    if database.verify_password("Group Closure", password):
        result = database.close_group_database(group_name, close_reason)
        if result:
            all_group_list = database.get_all_group_list()
            return render(request, 'group_master.html', {"Group_list": all_group_list})
    else:
        empty_group_list = database.get_empty_group_list()
        closed_group_list = database.get_closed_group_list()
        return render(request, 'close_group_list.html', {"Alert": "Error! Please check the password!",
                                                         "Empty_group_list": empty_group_list,
                                                         "Closed_group_list": closed_group_list})
    empty_group_list = database.get_empty_group_list()
    closed_group_list = database.get_closed_group_list()
    return render(request, 'close_group_list.html', {"Empty_group_list": empty_group_list,
                                                     "Closed_group_list": closed_group_list})


def new_client_code(request):
    groupId = request.POST.get('groupId', '')
    partyId = request.POST.get('partyId', '')

    if groupId != '' and partyId != '':
        party_detail = database.get_party_detail_from_id(partyId)
        client_list = database.get_all_distinct_clients_from_party_name(party_detail['Party_name'])
        group_name = database.get_group_name_from_id(groupId)
        it_no_list = database.get_all_distinct_value('It_no')
        audit_no_list = database.get_all_distinct_value('Audit_no')
        for client in client_list:
            client_type_form_name = client['Client_type']
            show_further = True
            it_start, it_end = database.get_it_no_range(group_name, client_type_form_name)
            audit_start, audit_end = database.get_audit_no_range(group_name, client_type_form_name)

            # convert it no from clientMaster to int
            it_no_list_int = [int(x) for x in it_no_list]
            audit_no_list_int = [int(x) for x in audit_no_list]
            it_no_range = [x for x in range(it_start, it_end + 1)]
            audit_no_range = [x for x in range(audit_start, audit_end + 1)]
            client['available_it_no'] = sorted(list(set(it_no_range) - set(it_no_list_int)))
            client['available_audit_no'] = sorted(list(set(audit_no_range) - set(audit_no_list_int)))
            client['_id'] = str(client['_id'])
        return JsonResponse(client_list, safe=False)

    else:
        data = {}
        return JsonResponse(data, safe=False)


def password_validate(request):
    operation_name = request.POST.get('operation')
    pwd = request.POST.get('password')
    is_password = database.verify_password(operation_name, pwd)
    if is_password:
        return JsonResponse({'Alert': "Correct"})
    else:
        return JsonResponse({'Alert': "InCorrect"})


def close_client(request):
    if request.method == 'POST':
        # Retrieve data sent from the frontend
        data = request.POST  # Assuming you sent the data as form data
        if database.verify_password("Client Closure", data['password']):

            success, message = database.close_client(data)
            response_data = {'message': message}
            if success == 1:
                return JsonResponse(response_data)
            else:
                return JsonResponse(response_data, status=500)
        else:
            response_data = {'message': 'Password is Incorrect'}
            return JsonResponse(response_data, status=500)

        # Handle other HTTP methods or errors
    return JsonResponse({'message': 'Invalid request method'}, status=400)


def check_client_name(request):
    client_name = request.GET.get('client_name')

    name_exist = database.check_client_name_present(client_name)
    return JsonResponse({'exists': name_exist})

