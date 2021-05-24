import ssl
import pymongo as pymongo
from django.shortcuts import render
from clients import database

# Create your views here.


def client_landing(request):
    return render(request, 'client_landing.html')


def client_master_list(request):
    all_return_list = database.get_client_master_list()
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

        if it_start == 0 or it_end == 0 or audit_start == 0 or audit_end == 0:
            return render(request, 'new_client.html')
        else:
            # convert it no from clientMaster to int
            it_no_list_int = [int(x) for x in it_no_list]
            audit_no_list_int = [int(x) for x in audit_no_list]
            it_no_range = [x for x in range(it_start, it_end + 1)]
            audit_no_range = [x for x in range(audit_start, audit_end + 1)]
            available_it_no = sorted(list(set(it_no_range) - set(it_no_list_int)))
            available_audit_no = sorted(list(set(audit_no_range) - set(audit_no_list_int)))
            return render(request, 'new_client.html', {'Show_Further': show_further,
                                                       'Available_It_No': available_it_no,
                                                       'Available_Audit_No': available_audit_no,
                                                       'Group_Selected': group_no,
                                                       'Type_Selected': client_type_form})
    return render(request, 'new_client.html')


def submit_new_client(request):
    client_name = request.POST.get('name')
    group_name = request.POST.get('groupName')
    party_name = request.POST.get('partyName')
    it_no = request.POST.get('itNo')
    cert_no = request.POST.get('certificateNo')
    audit_no = request.POST.get('auditNo')
    contact_list = []
    contact_names = request.POST.getlist('contactName')
    contact_nos = request.POST.getlist('contactNo')
    contact_designation = request.POST.getlist('contactDesignation')
    contact_emails = request.POST.getlist('contactEmail')

    for x in range(len(contact_names)):
        temp = {'Name': contact_names[x].upper(), 'Designation': contact_designation[x].upper(),
                'Contact_no': contact_nos[x], 'Email': contact_emails[x]}
        contact_list.append(temp)

    data_dict = {'Name': client_name.upper(),
                 'Group_name': group_name.upper(),
                 'Party_name': party_name.upper(),
                 'Client_code': it_no,
                 'It_no': it_no,
                 'Certificate_no': cert_no,
                 'Audit_no': audit_no,
                 'Contact_details': contact_list
                 }
    data_add = database.add_client_details(data_dict)
    return render(request, 'new_client.html')
