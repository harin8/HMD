from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from timesheet.database import get_user_timesheets_by_task_assignment
from accounts.database import get_user_profile_mongo
from reports.database import get_r_type_2
from costsheet.database import get_client_details_from_name, get_record_from_db

# Create your views here.


def generate_cost_sheet(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST request required'}, status=400)
    
    try:
        all_id = request.POST.get('ids', '').split(',')
        all_types = request.POST.get('types', '').split('^,^')

        if not all_id or not all_types:
            return JsonResponse({'error': 'No records or types provided'}, status=400)
        
        all_records = []
        # Process each record
        for record_id, record_type in zip(all_id, all_types):
            type_name = get_r_type_2(record_type)
            if type_name:
                record = get_record_from_db(record_id, type_name)
                if record:
                    # Add task and assignment fields for timesheet matching
                    record['task'] = type_name
                    client_details = get_client_details_from_name(record['Name'])
                    record['Party_name'] = client_details['Party_name']
                    record['Group_name'] = client_details['Group_name']
                    record['It_no'] = client_details['It_no']
                    record['Audit_no'] = client_details['Audit_no']
                    record['assignment_id'] = record_id
                    all_records.append(record)
        
        # Check if more than 1 unique clients are selected
        unique_clients = list(set(record['Name'] for record in all_records))
        if len(unique_clients) > 1:
            return JsonResponse({'error': 'Cannot select more than 2 clients at once'}, status=400)

        # Get timesheet entries for these records
        assignment_entries = {}
        for record in all_records:
            # Find timesheet entries matching this record's task and assignment
            entries = get_user_timesheets_by_task_assignment(
                assignment_id=record['assignment_id'],
            )
            # Create a key for this assignment
            assignment_key = f"{record['assignment_id']}"
            
            # Initialize the assignment entry if it doesn't exist
            if assignment_key not in assignment_entries:
                assignment_entries[assignment_key] = {
                    'task': record['task'],
                    'Name': record['Name'],
                    'Party_name': record['Party_name'],
                    'Group_name': record['Group_name'],
                    'It_no': record['It_no'],
                    'Audit_no': record['Audit_no'],
                    'assignment': entries[0]['assignment'] if entries else '',
                    'users': []
                }
            
            # Add users and their hours to this assignment
            for entry in entries:
                # Find the appropriate rate based on the timesheet date
                applicable_rate = None
                entry_date = entry['date']
                
                # Sort rate history by effective_date in descending order
                sorted_rates = sorted(entry['rate_history'], key=lambda x: x['effective_date'], reverse=True)
                
                # Find the first rate that was effective on or before the timesheet date
                for rate in sorted_rates:
                    if rate['effective_date'] <= entry_date:
                        applicable_rate = rate['hourly_rate']
                        break
                
                # If no applicable rate found, use the most recent rate
                if applicable_rate is None and sorted_rates:
                    applicable_rate = sorted_rates[0]['hourly_rate']
                
                user_entry = {
                    'user_name': entry['user_name'],
                    'hours': entry['hours'],
                    'designation': entry['designation'],
                    'rate': applicable_rate
                }
                assignment_entries[assignment_key]['users'].append(user_entry)

        # Convert the dictionary to a list for template rendering
        all_records = list(assignment_entries.values())
        
        return render(request, 'cost_sheet_result.html', {
            'client_name': all_records[0]['Name'],
            'party_name': all_records[0]['Party_name'],
            'group_name': all_records[0]['Group_name'],
            'it_no': all_records[0]['It_no'],
            'audit_no': all_records[0]['Audit_no'],
            'task': all_records[0]['task'],
            'assignment': all_records[0]['assignment'],
            'records': all_records
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
