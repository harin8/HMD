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
                                                       'Group_Selected': group_no,
                                                       'Type_Selected': client_type_form,
                                                       'Contact_List': contact_list,
                                                       'Party_List': party_list})
    return render(request, 'new_client.html')


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
    '''contact_nos = request.POST.getlist('contactNo')
    contact_emails = request.POST.getlist('contactEmail')'''
    if client_type != '' and group_name != '' and party_name != '':
        # check if it_code is already taken or not
        it_code_present = database.check_it_code_present(it_no)
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
    all_return_list = database.get_client_master_list(id_field=False)
    return render(request, 'client_master.html', {'client_List': all_return_list})


def edit_clients(request):
    render(request, 'client_master.html', {'Can_Edit': True})


def edit_contact(request, id):
    contact_detail = contact_database.get_contact_detail_from_id(id)
    if contact_detail:
        return render(request, 'create_new_contact.html', {'Hide': True, 'Contact_Details': contact_detail})


def party_master_list(request):
    party_size = database.get_client_it_size_list()

    return render(request, 'party_master.html', {'Party_Size': party_size})


def create_new_party(request):
    return render(request, 'new_party.html')


def submit_new_party(request):
    group_no = request.POST.get('GroupNameForm', '')
    party_name = request.POST.get('partyName', '')
    group_name = database.get_group_name_from_id(group_no)
    if group_no != '' and party_name != '':
        data_dict = {'Group_name': group_name.upper(),
                     'Party_name': party_name.upper(),
                     }
        data_add = database.add_party_details(data_dict)
    party_size = database.get_client_it_size_list()
    return render(request, 'party_master.html', {'Party_Size': party_size})


def edit_party_list(request):
    party_list = database.get_party_master_list(id_field=True)
    return render(request, 'party_master.html', {'can_edit': True, 'Party_List': party_list})


def edit_party(request, id):
    party_detail = database.get_party_detail_from_id(id)
    if party_detail:
        group_code = database.get_group_code_from_group_name(party_detail['Group_name'])
        return render(request, 'new_party.html', {'Hide': True, 'G_Code': group_code, 'Party_Details': party_detail})

    return render(request, 'new_party.html')


def submit_edit_party(request):
    r_id = request.POST.get('r_id')
    group_no = request.POST.get('GroupNameForm', '')
    party_name = request.POST.get('partyName', '')
    group_name = database.get_group_name_from_id(group_no)
    party_detail = database.get_party_detail_from_id(r_id)

    if group_no != '' and party_name != '':
        data_dict = {'Group_name': group_name.upper(),
                     'Party_name': party_name.upper(),
                     }
        data_update = database.update_party_details(r_id, data_dict)
        party_list = database.get_party_master_list(id_field=True)
        return render(request, 'party_master.html', {'can_edit': True, 'Party_List': party_list})
    return render(request, 'new_party.html', {'Error': True, 'Hide': True, 'Party_Details': party_detail})