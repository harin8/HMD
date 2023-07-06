from . import database


def get_selected_tasks(form_data_dict):
    task_list = []
    selected_task_list = form_data_dict.getlist('task')
    if 'ROI' in selected_task_list:
        task_list.append('ROI')
    if 'Certificates' in selected_task_list:
        task_list.append('Certificates')
    if 'Other' in selected_task_list:
        task_list.append('Other')
    if 'TDS' in selected_task_list:
        task_list.append('TDS')
    if 'Proceedings' in selected_task_list:
        task_list.append('Proceedings')

    return task_list


def get_period(form_data_dict, task_list):
    period_list = {}
    if "ROI" in task_list:
        ay = form_data_dict.getlist('A.Y')
        period_list['ROI'] = ay
    if "Certificates" in task_list:
        cert_start_date = form_data_dict['certificateStartDate']
        period_list['Certificates'] = {'Start_date': cert_start_date}
    if "Other" in task_list:
        cert_start_date = form_data_dict['otherFormsStartDate']
        period_list['Other'] = {'Start_date': cert_start_date}
    if "TDS" in task_list:
        tds_ay = form_data_dict.getlist('tds')
        period_list['TDS'] = tds_ay
    if "Proceedings" in task_list:
        proceedings_ay = form_data_dict.getlist('proceedings')
        period_list['Proceedings'] = proceedings_ay

    return period_list


def get_group_name(form_data_dict):
    group_name_list = []
    selected_group_list = form_data_dict.getlist('groupName')
    if "ESD-DHD" in selected_group_list:
        group_name_list.append("ESD-DHD")
    if "ESD-NRJ" in selected_group_list:
        group_name_list.append("ESD-NRJ")
    if "RIS" in selected_group_list:
        group_name_list.append("RIS")
    if "VHD" in selected_group_list:
        group_name_list.append("VHD")
    if "PRB" in selected_group_list:
        group_name_list.append("PRB")
    if "OS-ESD" in selected_group_list:
        group_name_list.append("OS-ESD")
    if "OS-RIS" in selected_group_list:
        group_name_list.append("OS-RIS")
    if "OS-VHD" in selected_group_list:
        group_name_list.append("OS-VHD")
    if "OS-PRB" in selected_group_list:
        group_name_list.append("OS-PRB")
    return group_name_list


def get_party_name(form_data_dict):
    selected_party_list = form_data_dict.getlist('partyName')
    return selected_party_list
