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
    password = request.POST.get('password', '')
    for x in range(len(name)):
        if name[x] == 'NA':
            return render(request, 'create_new_forum_author.html', {'Error': True})
        temp = {'Name': name[x].upper()}
        if_name_exists = database.check_if_contact_name_exists(temp['Name'])
        if if_name_exists:
            message = temp['Name'] + ' name already exists in DB'
            return render(request, 'create_new_forum_author.html', {'Error': True, 'Alert': message})
    if database.verify_password("Forum Author Creation", password):
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
        return render(request, 'create_new_forum_author.html', {'Alert': 'Error! Please check the password!'})


def forum_author_master_list(request):
    forum_author_list = database.get_all_forum_author_details()
    return render(request, 'forum_author_master.html', {'forum_author_list': forum_author_list})


def create_new_certificate_description(request):
    return render(request, 'create_new_certificate_description.html')


def submit_new_certificate_description(request):
    certificate_description_list = []
    name = request.POST.getlist('Name', 'NA')
    password = request.POST.get('password', '')
    for x in range(len(name)):
        if name[x] == 'NA':
            return render(request, 'create_new_certificate_description.html',
                          {'Error': True, 'Alert': 'Error! Please give proper name!'})
        temp = {'Name': name[x].upper()}
        if_name_exists = database.check_if_certificate_description_exists(temp['Name'])
        if if_name_exists:
            message = temp['Name'] + ': This certificate description already exists in DB'
            return render(request, 'create_new_certificate_description.html', {'Error': True, 'Alert': message})
    if database.verify_password("Forum Author Creation", password):
        for x in range(len(name)):
            temp = {'Name': name[x].upper()}
            certificate_description_list.append(temp)
        try:
            data_add = database.add_certificate_description(certificate_description_list)
            certificate_description_list = database.get_all_certificate_description(id=False)
            return render(request, 'certificate_description_master.html',
                          {'certificate_description_list': certificate_description_list[0]})
        except TypeError:
            return render(request, 'create_new_certificate_description.html', {'Error': True})
    else:
        return render(request, 'create_new_certificate_description.html',
                      {'Alert': 'Error! Please check the password!'})


def certificate_description_master_list(request):
    certificate_description_list = database.get_all_certificate_description(id=False)
    return render(request, 'certificate_description_master.html',
                  {'certificate_description_list': certificate_description_list[0]})


def create_new_other_form_description(request):
    return render(request, 'create_new_other_form_description.html')


def submit_new_other_form_description(request):
    other_form_description_list = []
    name = request.POST.getlist('Name', 'NA')
    password = request.POST.get('password', '')
    for x in range(len(name)):
        if name[x] == 'NA':
            return render(request, 'create_new_other_form_description.html',
                          {'Error': True, 'Alert': 'Error! Please give proper name!'})
        temp = {'Name': name[x].upper()}
        if_name_exists = database.check_if_other_form_description_exists(temp['Name'])
        if if_name_exists:
            message = temp['Name'] + ': This Other Form description already exists in DB'
            return render(request, 'create_new_other_form_description.html', {'Error': True, 'Alert': message})
    if database.verify_password("Forum Author Creation", password):
        for x in range(len(name)):
            temp = {'Name': name[x].upper()}
            other_form_description_list.append(temp)
        try:
            data_add = database.add_other_form_description(other_form_description_list)
            other_form_description_list = database.get_all_other_form_description(id=False)
            return render(request, 'other_form_description_master.html',
                          {'other_form_description_list': other_form_description_list[0]})
        except TypeError:
            return render(request, 'create_new_other_form_description.html', {'Error': True})
    else:
        return render(request, 'create_new_other_form_description.html', {'Alert': 'Error! Please check the password!'})


def other_form_description_master_list(request):
    other_form_description_list = database.get_all_other_form_description(id=False)
    return render(request, 'other_form_description_master.html',
                  {'other_form_description_list': other_form_description_list[0]})


def create_new_proceedings_description(request):
    return render(request, 'create_new_proceedings_description.html')


def submit_new_proceedings_description(request):
    proceedings_description_list = []
    type = request.POST.getlist('Type', 'NA')
    name = request.POST.getlist('Name', 'NA')
    password = request.POST.get('password', '')
    if len(type) != len(name):
        return render(request, 'create_new_proceedings_description.html',
                      {'Error': True, 'Alert': 'Error! Please select type of proceeding!'})
    for x in range(len(name)):
        if name[x] == 'NA':
            return render(request, 'create_new_proceedings_description.html',
                          {'Error': True, 'Alert': 'Error! Please give proper description!'})
        if type[x] == "NA":
            return render(request, 'create_new_proceedings_description.html',
                          {'Alert': 'Error! Please select type of proceeding!'})
        temp = {'Name': name[x].upper(),
                'Type': type[x]}
        if_name_exists = database.check_if_proceedings_description_exists(temp['Name'], temp['Type'])
        if if_name_exists:
            message = temp['Name'] + ': This Proceeding description already exists in DB'
            return render(request, 'create_new_proceedings_description.html', {'Error': True, 'Alert': message})

    if database.verify_password("Forum Author Creation", password):
        for x in range(len(type)):
            temp = {'Name': name[x].upper(),
                    'Type': type[x]}
            proceedings_description_list.append(temp)
        try:
            data_add = database.add_proceedings_description(proceedings_description_list)
            proceedings_description_list = database.get_all_proceedings_description(id=False)
            return render(request, 'proceedings_description_master.html',
                          {'proceedings_description_list': proceedings_description_list})
        except TypeError:
            return render(request, 'create_new_proceedings_description.html', {'Error': True})
    else:
        return render(request, 'create_new_proceedings_description.html',
                      {'Alert': 'Error! Please check the password!'})


def proceedings_description_master_list(request):
    proceedings_description_list = database.get_all_proceedings_description(id=False)
    return render(request, 'proceedings_description_master.html',
                  {'proceedings_description_list': proceedings_description_list})


def delete_proceedings_description(request, p_no, p_type):
    # check if exists in db
    if database.check_if_proceedings_description_exists_by_name(p_no, p_type):
        database.delete_proceedings_description(p_no, p_type)
        proceedings_description_list = database.get_all_proceedings_description(id=False)
        return render(request, 'proceedings_description_master.html',
                      {'proceedings_description_list': proceedings_description_list,
                       'Message': 'Proceeding Description deleted successfully!'})
    proceedings_description_list = database.get_all_proceedings_description(id=False)
    return render(request, 'proceedings_description_master.html',
                  {'proceedings_description_list': proceedings_description_list})


def delete_other_form_description(request, p_no):
    # check if exists in db
    if database.check_if_other_form_description_exists_by_name(p_no):
        database.delete_other_form_description(p_no)
        other_form_description_list = database.get_all_other_form_description(id=False)
        return render(request, 'other_form_description_master.html',
                      {'other_form_description_list': other_form_description_list[0],
                       'Message': 'Other Form Description deleted successfully!'})
    other_form_description_list = database.get_all_other_form_description(id=False)
    return render(request, 'other_form_description_master.html',
                  {'other_form_description_list': other_form_description_list[0]})


def delete_certificate_description(request, p_no):
    # check if exists in db
    if database.check_if_certificate_description_exists_by_name(p_no):
        database.delete_certificate_description(p_no)
        certificate_description_list = database.get_all_certificate_description(id=False)
        return render(request, 'certificate_description_master.html',
                      {'certificate_description_list': certificate_description_list[0],
                       'Message': 'Certificate Description deleted successfully!'})
    certificate_description_list = database.get_all_certificate_description(id=False)
    return render(request, 'certificate_description_master.html',
                  {'certificate_description_list': certificate_description_list[0]})