from typing import List, Any
import os
from django.shortcuts import render
from . import database
from django.core.files.storage import FileSystemStorage
import datetime
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseNotFound
from itertools import product
# Create your views here.


def landing(request):
    ay = request.GET.get('A.Y')
    ay_list = database.get_ay_list()
    judg_list = database.get_all_judgments_list()
    forum_author_list = database.get_all_forum_author_list()
    if ay:
        return render(request, 'landing_j.html',
                      {'AY_List': ay_list,  'Judg_list': judg_list, 'Forum_author_list' : forum_author_list})
    else:
        return render(request, 'landing_j.html',
                      {'AY_list': ay_list,  'Judg_list': judg_list, 'Forum_author_list' : forum_author_list})


def submit_judgments(request):
    ay = request.GET.get('A.Y')
    ay_list = database.get_ay_list()
    Type = request.POST.get('Type')
    Subject = request.POST.get('Subject')
    Section = request.POST.get('Section')
    Case_Title = request.POST.get('Case_Title')
    Citation = request.POST.get('Citation')
    forumAuthor = request.POST.get('forumAuthor')
    judgDate = request.POST.get('judgDate')
    AY = request.POST.get('AY')

    data_dict = {
        'Type': Type.upper(),
        'Subject': Subject.upper(),
        'Section': Section.upper(),
        'Case_Title': Case_Title.upper(),
        'Citation': Citation.upper(),
        'AY': AY.upper(),
        'forumAuthor': forumAuthor.upper(),
        'Judgment_Article_Date': judgDate.upper(),
        'Submitted_ini': True,
        'Status': '',
        'Summary': 0,
        'File': 0,
        'Catch_Phrase' : ''
    }
    return_result = database.add_judgments_data_in_db(data_dict)
   
    ay = request.GET.get('A.Y')
    ay_list = database.get_ay_list()
    judg_list = database.get_all_judgments_list()
    forum_author_list = database.get_all_forum_author_list()
    if ay:
        return render(request, 'landing_j.html',
                      {'AY_List': ay_list,  'Judg_list': judg_list, 'Forum_author_list' : forum_author_list})
    else:
        return render(request, 'landing_j.html',
                      {'AY_list': ay_list,  'Judg_list': judg_list, 'Forum_author_list' : forum_author_list})



def further_judg_info(request, id):
    exist_result = database.get_judg_details(id)
    summary = exist_result['Summary']
    if exist_result:
        if summary == 0:
            return render(request, 'further_judg_info.html', {'Data_Dict': exist_result})
        else:
            summary_result = database.get_summary_details_further_judg(id)
            return render(request, 'further_judg_info.html', {'Data_Dict': exist_result, 'Summary_result': summary_result})

    judg_list = database.get_all_judgments_list()

    return render(request, 'landing_j.html', { 'Judg_list': judg_list})

def submit_judg_summaries(request):
    r_id = request.POST.get('Record_Id')
    Catch_Phrase = request.POST.get('Catch_Phrase')
    Held_Discussion = request.POST.get('Held_Discussion')
    Our_Remarks = request.POST.get('Our_Remarks')
    Remarks_By = request.POST.get('Remarks_By')

    data_dict = {
        'Judg_id': r_id,
        'Catch_Phrase': Catch_Phrase.upper(),
        'Held_Discussion': Held_Discussion.upper(),
        'Our_Remarks': Our_Remarks.upper(),
        'Remarks_By': Remarks_By.upper()

    }
    result = database.add_summary_details(data_dict)

    catch_phrase_list = []
    summary_list = database.get_summary_details_further_judg(str(r_id))
    for each_sum in summary_list:
        catch_phrase_list.append(str(each_sum["Catch_Phrase"]).upper())
    if catch_phrase_list.__len__ == 0:
            catch_phrase_list.insert(0,Catch_Phrase.upper()) 
    data_dict = {
        'Summary': 1,
        'Catch_Phrase_List' : ','.join(catch_phrase_list) 
    }
    data_update = database.update_judg_details(r_id, data_dict)
    return further_judg_info(request, r_id)

def submit_judg_Citation(request):
    r_id = request.POST.get('Record_Id')
    Citation = request.POST.get('Citation')
    data_dict = {
                'Citation': Citation.upper()
            }
    data_update = database.update_judg_details(r_id, data_dict)
    return further_judg_info(request, r_id)

def submit_judg_File(request):
     r_id = request.POST.get('Record_Id')
     if request.FILES['myfile']:
                data_dict = {
                    'File': 1
                }
                data_update = database.update_judg_details(r_id, data_dict)
                myfile = request.FILES['myfile']
                now = datetime.now()
                date_time = now.strftime("%m%d%Y%H%M%S")
                only_file_name = myfile.name.rsplit('.',1)[0]+date_time
                file = only_file_name+"."+myfile.name.rsplit('.', 1)[1]
                print(file)
                file_data = {
                    'File_name': file
                }
                file_update = database.add_further_judg_file_record(file_data, r_id)
                fs = FileSystemStorage()
                filename = fs.save(file, myfile)
                uploaded_file_url = fs.url(file)
     return further_judg_info(request, r_id)

def summary_landing(request, id):
    exist_result = database.get_judg_for_summary_details(id)

    summary_list = database.get_summary_details(id)
    print(summary_list)

    return render(request, 'summary_landing.html', {'Data_Dict': exist_result, 'Summary_list': summary_list})


def pdf_view(request, id):
    fs = FileSystemStorage()
    exist_result = database.get_judg_details(id)
    filename = exist_result['File_name']
    print(filename)
    print(exist_result['File_name'])
    if fs.exists(filename):
        with fs.open(filename) as pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            # response['Content-Disposition'] = 'attachment; filename="mypdf.pdf"' #user will be prompted with the browser’s open/save file
            response[
                'Content-Disposition'] = 'inline; filename="KARAN03132022015234.pdf"'  # user will be prompted display the PDF in the browser
            return response
    else:
        return HttpResponseNotFound('The requested pdf was not found.')