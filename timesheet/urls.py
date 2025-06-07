from django.urls import path
from . import views

urlpatterns = [
    path('fill/', views.fill_timesheet, name='fill_timesheet'),
    path('get-assignments/', views.get_assignments, name='get_assignments'),
    path('calculate-hours/', views.calculate_hours, name='calculate_hours'),
    path('employee-corner/', views.employee_corner, name='employee_corner'),
    path('get-time-settings/', views.get_time_settings, name='get_time_settings'),
    path('delete-entry/', views.delete_timesheet_entry, name='delete_timesheet_entry'),
    path('get_pending_entries/', views.get_pending_entries, name='get_pending_entries')
]