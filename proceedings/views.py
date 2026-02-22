import os
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import render, redirect

from . import database
import clients.database as client_database


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _proceedings_context(request, proc_type, list_fn, template, cert_desc_fn=None):
    """Build and render a proceedings landing page response.

    Args:
        request:       The HTTP request.
        proc_type:     Proceeding type integer (1 = Regular, 2 = Judicial, 3 = Other).
        list_fn:       Callable that returns the list of proceedings records.
        template:      Template name to render.
        cert_desc_fn:  Optional callable returning certificate description mapping.
    """
    ay_list = database.get_ay_list()
    all_client_list = database.get_all_clients_details()
    proc_list = list_fn()

    for data in proc_list:
        data['Client_code'] = database.get_client_code_from_name(data['Name'])
        data['Group_name'] = database.get_group_name_from_client_name(data['Name'])

    context = {
        'AY_list': ay_list,
        'Client_list': all_client_list,
        'Proc_list': proc_list,
    }
    if cert_desc_fn:
        context['Cert_Desc'] = cert_desc_fn()

    return render(request, template, context)


def _landing_response_for_type(request, proc_type):
    """Return the correct landing page response based on proceeding type."""
    if proc_type == 1:
        return regular_proceedings_landing(request)
    if proc_type == 2:
        return judicial_proceedings_landing(request)
    return landing(request)


def _create_proceeding(request, proc_type):
    """Shared logic for creating a new proceeding of any type."""
    client_code = request.POST.get('Client_Code', '')
    base_date = request.POST.get('Base_Date', '')
    description = request.POST.get('Description', '')
    section = request.POST.get('Section', '')
    base_document = request.POST.get('Base_Document', '')
    led_by = request.POST.get('Led_By', '')
    ay = request.POST.get('AY', '')

    valid_client, db_client_name = database.check_client_from_client_code(client_code)

    if valid_client:
        data_dict = {
            'Name': db_client_name,
            'Base_document': base_document.upper(),
            'Led_by': led_by.upper(),
            'Base_date': base_date,
            'Description': description.upper(),
            'AY': ay,
            'Type': proc_type,
            'Section': section,
            'Submitted_ini': True,
            'Forum_bench': '',
            'Status': '',
            'Case_reference_no': '',
            'Event': 0,
        }
        database.add_proceedings_data_in_db(data_dict)


# ---------------------------------------------------------------------------
# Landing views
# ---------------------------------------------------------------------------

@login_required
def landing(request):
    return _proceedings_context(
        request,
        proc_type=3,
        list_fn=database.get_all_proceedings_list,
        template='landing_p.html',
    )


@login_required
def judicial_proceedings_landing(request):
    return _proceedings_context(
        request,
        proc_type=2,
        list_fn=database.get_all_judicial_proceedings_list,
        template='landing_jp.html',
        cert_desc_fn=database.initialise_juddescription_id_mapping,
    )


@login_required
def regular_proceedings_landing(request):
    return _proceedings_context(
        request,
        proc_type=1,
        list_fn=database.get_all_regular_proceedings_list,
        template='landing_rp.html',
        cert_desc_fn=database.initialise_regdescription_id_mapping,
    )


# ---------------------------------------------------------------------------
# Create-proceedings submit views
# ---------------------------------------------------------------------------

@login_required
def submit_proceedings(request):
    _create_proceeding(request, proc_type=3)
    return landing(request)


@login_required
def submit_judicial_proceedings(request):
    _create_proceeding(request, proc_type=2)
    return judicial_proceedings_landing(request)


@login_required
def submit_regular_proceedings(request):
    _create_proceeding(request, proc_type=1)
    return regular_proceedings_landing(request)


# ---------------------------------------------------------------------------
# Further proceedings detail
# ---------------------------------------------------------------------------

@login_required
def further_proc_info(request, id):
    exist_result = database.get_proc_details(id)
    exist_result['Client_code'] = database.get_client_code_from_name(exist_result['Name'])
    exist_result['Group_name'] = database.get_group_name_from_client_name(exist_result['Name'])
    exist_result['is_marked'] = database.is_case_marked_by_user(id, request.user.id)

    if exist_result['Event'] == 0:
        return render(request, 'further_proc_info.html', {'Data_Dict': exist_result})

    event_result = database.get_event_details_further_proc(id)
    return render(request, 'further_proc_info.html', {
        'Data_Dict': exist_result,
        'Event_list': event_result,
    })


@login_required
def further_proc_submit(request):
    r_id = request.POST.get('Record_Id')
    form_type = request.POST.get('Type')
    exist_result = database.get_proc_details(r_id)
    led_by = request.POST.get('Led_By', '')

    if form_type == '1':
        forum_bench = request.POST.get('Forum_Bench') or ''
        case_reference_no = request.POST.get('Case_Reference_no') or ''
        closure_due_date = request.POST.get('Closure_Due_Date') or ''

        database.update_proc_details(r_id, {
            'Forum_bench': forum_bench.upper(),
            'Case_reference_no': case_reference_no.upper(),
            'Led_by': led_by.upper(),
            'Closure_due_date': closure_due_date,
        })
        return further_proc_info(request, r_id)

    if form_type == '2':
        status = exist_result['Status']
        proc_type = exist_result['Type']

        if status != 'Completed':
            database.add_further_proc_record({
                'Closure_date': request.POST.get('Closure_Date'),
                'Actual_closure_date': request.POST.get('Actual_Closure_Date'),
                'Closure_type': request.POST.get('Closure_Type'),
                'Closure_particulars': request.POST.get('Closure_Particulars', '').upper(),
                'Closure_handled_by': request.POST.get('Closure_Handled_By', '').upper(),
                'Closure_remarks': request.POST.get('Closure_Remarks', '').upper(),
                'Status': 'Completed',
            }, r_id)

            try:
                myfile = request.FILES['myfile']
                now = datetime.now()
                date_time = now.strftime('%m%d%Y%H%M%S')
                name, ext = myfile.name.rsplit('.', 1)
                file_name = f'{name}{date_time}.{ext}'
                database.add_further_proc_file_record({'File_name': file_name}, r_id)
                fs = FileSystemStorage()
                fs.save(file_name, myfile)
            except (KeyError, Exception):
                pass

            close_proceedings = request.POST.get('close_proceedings')
            if close_proceedings == 'Yes':
                return judicial_proceedings_landing(request)
            if close_proceedings == 'No':
                return _landing_response_for_type(request, proc_type)

        if status == 'Completed':
            database.update_proc_details(r_id, {
                'Closure_remarks': request.POST.get('Closure_Remarks', '').upper(),
            })
            return _landing_response_for_type(request, proc_type)


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

@login_required
def submit_proceedings_events(request):
    r_id = request.POST.get('Record_Id')
    event_next_date = request.POST.get('Event_Next_date')
    event_particulars = request.POST.get('Event_Particulars', '')
    event_remarks = request.POST.get('Event_Remarks', '')

    database.add_event_details({
        'Proceeding_id': r_id,
        'Event_handled_by': request.POST.get('Event_Handled_By', '').upper(),
        'Event_type': request.POST.get('Event_type', '').upper(),
        'Event_remarks': event_remarks.upper(),
        'Event_particulars': event_particulars.upper(),
        'Event_date': request.POST.get('Event_Date'),
        'Event_actual_date': request.POST.get('Event_Actual_Date'),
        'Event_next_date': event_next_date,
    })

    database.add_further_proc_record({
        'Closure_date': event_next_date,
        'Closure_particulars': event_particulars.upper(),
        'Closure_remarks': event_remarks.upper(),
    }, r_id)

    database.update_proc_details(r_id, {
        'Event': 1,
        'Event_actual_date': request.POST.get('Event_Actual_Date'),
    })

    return further_proc_info(request, r_id)


@login_required
def event_landing(request, id):
    exist_result = database.get_proc_for_event_details(id)
    exist_result['Client_code'] = database.get_client_code_from_name(exist_result['Name'])
    exist_result['Group_name'] = database.get_group_name_from_client_name(exist_result['Name'])
    event_result = database.get_event_details(id)
    return render(request, 'event_landing.html', {'Data_Dict': exist_result, 'Event_list': event_result})


# ---------------------------------------------------------------------------
# Mark / Unmark case
# ---------------------------------------------------------------------------

@login_required
def mark_case(request):
    """Toggle a proceedings case as marked/unmarked for quick access."""
    if request.method != 'POST':
        return JsonResponse({'success': False}, status=400)

    proceeding_id = request.POST.get('proceeding_id')
    action = request.POST.get('action')  # 'mark' or 'unmark'
    username = request.user.id

    if action == 'mark':
        success = database.mark_proceedings_case(proceeding_id, username)
    else:
        success = database.unmark_proceedings_case(proceeding_id, username)

    return JsonResponse({'success': success})


# ---------------------------------------------------------------------------
# PDF / File viewer
# ---------------------------------------------------------------------------

@login_required
def pdf_view(request, id):
    fs = FileSystemStorage()
    exist_result = database.get_proc_details(id)
    filename = exist_result.get('File_name', '')

    if fs.exists(filename):
        with fs.open(filename) as pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{filename}"'
            return response

    return HttpResponseNotFound('The requested PDF was not found.')


# ---------------------------------------------------------------------------
# Delete proceedings
# ---------------------------------------------------------------------------

@login_required
def delete_proceedings(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

    password = request.POST.get('password')
    proc_id = request.POST.get('proceedingId')

    if not client_database.verify_password('Record Delete', password):
        return JsonResponse({'status': 'error', 'message': 'Incorrect password.'}, status=403)

    if database.delete_proceedings_record(proc_id):
        return JsonResponse({'status': 'success', 'message': 'Record deleted successfully.'})

    return JsonResponse({'status': 'error', 'message': 'Record not found.'}, status=404)
