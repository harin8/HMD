def get_selected_tasks(form_data_dict):
    task_list = []
    try:
        roi = form_data_dict['ROI']
        task_list.append(roi)
    except:
        pass
    try:
        cert = form_data_dict['Cert']
        task_list.append(cert)
    except:
        pass
    try:
        other = form_data_dict['Other']
        task_list.append(other)
    except:
        pass

    return task_list


def get_period(form_data_dict, task_list):
    period_list = {}
    if "ROI" in task_list:
        ay = form_data_dict['A.Y']
        period_list['ROI'] = ay
    if "Certificates" in task_list:
        cert_start_date = form_data_dict['certificateStartDate']
        period_list['Certificates'] = {'Start_date': cert_start_date}
    if "otherForms" in task_list:
        cert_start_date = form_data_dict['otherFormsStartDate']
        period_list['OtherForms'] = {'Start_date': cert_start_date}

    return period_list


def get_group_name(form_data_dict):
    group_name_list = []
    if "ESD" in form_data_dict:
        group_name_list.append("ESD")
    if "RIS" in form_data_dict:
        group_name_list.append("RIS")
    if "VHD" in form_data_dict:
        group_name_list.append("VHD")
    if "PRB" in form_data_dict:
        group_name_list.append("PRB")
    if "OS-ESD" in form_data_dict:
        group_name_list.append("OS-ESD")
    if "OS-RIS" in form_data_dict:
        group_name_list.append("OS-RIS")
    if "OS-VHD" in form_data_dict:
        group_name_list.append("OS-VHD")
    if "OS-PRB" in form_data_dict:
        group_name_list.append("OS-PRB")

    return group_name_list
