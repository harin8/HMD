from django.shortcuts import render
from insertions import database


# Create your views here.

def landing(request):
    return render(request, 'insertions_landing.html')


def create_new_forum_author(request):
    return render(request, 'create_new_forum_author.html')


def submit_new_forum_author(request):
    forum_author_list = []
    type = request.POST.getlist('Type', 'NA')
    name = request.POST.getlist('Name', 'NA')
    password= request.POST.get('password', '')
    for x in range(len(name)):
        if name[x] == 'NA':
            return render(request, 'create_new_contact.html', {'Error': True})
        temp = {'Name': name[x].upper()}
        if_name_exists = database.check_if_contact_name_exists(temp['Name'])
        if if_name_exists:
            message = temp['Name'] + ' name already exists in DB'
            return render(request, 'create_new_forum_author.html', {'Error': True, 'Alert':  message})
    if password == 'HMDDIWAN':
        for x in range(len(type)):
            if type[x] == 'NA':
                return render(request, 'create_new_forum_author.html', {'Error': True})
            temp = {'Type': type[x].upper(),
                    'Name': name[x].upper()}
        
            forum_author_list.append(temp)
        try:
            data_add = database.add_forum_author_details(forum_author_list)
            forum_author_list = database.get_all_forum_author_details()
            return render(request, 'forum_author_master.html', {'forum_author_list': forum_author_list})
        except TypeError:
            return render(request, 'create_new_forum_author.html', {'Error': True})
    else:   
        return render(request, 'create_new_forum_author.html',{'Alert': 'Error! Please check the password!'})


def edit_contacts(request):
    contact_list = database.get_all_forum_author_details()
    return render(request, 'forum_author_master.html', {'can_edit': True, 'contact_list': contact_list})


def forum_author_master_list(request):
    forum_author_list = database.get_all_forum_author_details()
    return render(request, 'forum_author_master.html', {'forum_author_list': forum_author_list})


def edit_contact(request, id):
    contact_detail = database.get_contact_detail_from_id(id)
    if contact_detail:
        return render(request, 'create_new_contact.html', {'Hide': True, 'Contact_Details': contact_detail})
    contact_list = database.get_all_forum_author_details()
    return render(request, 'forum_author_master.html', {'contact_list': contact_list})


def submit_edit_contact(request):
    r_id = request.POST.get('r_id')

    contact_detail = database.get_contact_detail_from_id(r_id)

    contact_name = request.POST.get('contactName','NA').upper()
    contact_no = request.POST.get('contactNo','NA')
    contact_email = request.POST.get('contactEmail','NA')
    contact_remark = request.POST.get('remarks','').upper()

    if contact_detail:
        temp = {'Name': contact_name,
                'Contact_no': contact_no, 'Email': contact_email, 'Remarks': contact_remark}
        if_name_exists = database.check_if_contact_name_exists(temp['Name'])
        if if_name_exists:
            message = temp['Name'] + ' name already exists in DB'
            return render(request, 'create_new_contact.html', {'Error': True, 'Message': message, 'Hide': True,
                                                               'Contact_Details': contact_detail})
        data_update = database.update_contact_details(r_id, temp)
        # update contact detail in clientMasterDB
        client_contact_update = database.update_contact_details_in_clientMaster(r_id, temp)
        contact_detail = database.get_contact_detail_from_id(r_id)
        contact_list = database.get_all_forum_author_details()
        return render(request, 'forum_author_master.html', {'can_edit': True, 'contact_list': contact_list})
    return render(request, 'create_new_contact.html', {'Error': True, 'Hide': True, 'Contact_Details': contact_detail})