from django.shortcuts import render
from contacts import database


# Create your views here.

def landing(request):
    return render(request, 'contacts_landing.html')


def create_new_contact(request):
    return render(request, 'create_new_contact.html')


def submit_new_contact(request):
    contact_list = []
    contact_names = request.POST.getlist('contactName')
    contact_nos = request.POST.getlist('contactNo')
    contact_emails = request.POST.getlist('contactEmail')
    contact_remarks = request.POST.getlist('remarks')

    for x in range(len(contact_names)):
        temp = {'Name': contact_names[x].upper(),
                'Contact_no': contact_nos[x], 'Email': contact_emails[x], 'Remarks': contact_remarks[x].upper()}
        # check if already exists in db
        if_exists = database.get_contact_detail_from_name_no(temp['Name'], temp['Contact_no'])
        if if_exists:
            continue
        contact_list.append(temp)
    try:
        data_add = database.add_contact_details(contact_list)
    except TypeError:
        return render(request, 'create_new_contact.html', {'Error': True})
    return render(request, 'create_new_contact.html')


def edit_contacts(request):
    contact_list = database.get_all_contact_details()
    return render(request, 'contact_master.html', {'can_edit': True, 'contact_list': contact_list})


def contact_master_list(request):
    contact_list = database.get_all_contact_details()
    return render(request, 'contact_master.html', {'contact_list': contact_list})


def edit_contact(request, id):
    contact_detail = database.get_contact_detail_from_id(id)
    if contact_detail:
        return render(request, 'create_new_contact.html', {'Hide': True, 'Contact_Details': contact_detail})


def submit_edit_contact(request):
    r_id = request.POST.get('r_id')

    contact_detail = database.get_contact_detail_from_id(r_id)

    contact_name = request.POST.get('contactName').upper()
    contact_no = request.POST.get('contactNo')
    contact_email = request.POST.get('contactEmail')
    contact_remark = request.POST.get('remarks').upper()

    if contact_detail:
        temp = {'Name': contact_name,
                'Contact_no': contact_no, 'Email': contact_email, 'Remarks': contact_remark}
        data_update = database.update_contact_details(r_id, temp)
        contact_detail = database.get_contact_detail_from_id(r_id)
        return render(request, 'create_new_contact.html', {'Hide': True, 'Contact_Details': contact_detail})
    return render(request, 'create_new_contact.html', {'Hide': True, 'Contact_Details': contact_detail})