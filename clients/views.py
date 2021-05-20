import ssl
import pymongo as pymongo
from django.shortcuts import render
from clients import database

__MONGO_CONNECTION_URI__ = 'mongodb://localhost/'

# __MONGO_CONNECTION_URI__ = 'mongodb+srv://Dhruvang:Diwan@cluster0.xp0yp.mongodb.net/test?retryWrites=true&w
# =majority&ssl=true'


client = pymongo.MongoClient(__MONGO_CONNECTION_URI__, 27017)
# client = pymongo.MongoClient(__MONGO_CONNECTION_URI__, ssl_cert_reqs=ssl.CERT_NONE)
db = client.HMD


# Create your views here.


def client_landing(request):
    return render(request, 'client_landing.html')


def client_master_list(request):
    all_return_list = database.get_client_master_list()
    return render(request, 'client_master.html', {'client_List': all_return_list})


def create_new_client(request):
    client_code_list = database.get_all_distinct_value('Client_code')
    it_no_list = database.get_all_distinct_value('It_no')
    audit_no_list = database.get_all_distinct_value('Audit_no')
    certificate_no_list = database.get_all_distinct_value('Certificate_no')
    return render(request, 'new_client.html', {'Client_Code': client_code_list, 'It_No': it_no_list,
                                               'Audit_No': audit_no_list, 'Certificate_No': certificate_no_list})


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
        temp = {'Name': contact_names[x], 'Designation': contact_designation[x],
                'Contact_no': contact_nos[x], 'Email': contact_emails[x]}
        contact_list.append(temp)

    data_dict = {'Name': client_name,
                 'Group_name': group_name,
                 'Party_name': party_name,
                 'Client_code': it_no,
                 'It_no': it_no,
                 'Certificate_no': cert_no,
                 'Audit_no': audit_no,
                 'Contact_details': contact_list
                 }

    data_add = database.add_client_details(data_dict)
    return render(request, 'new_client.html')
