from django.urls import path

from . import views

urlpatterns = [
    path('', views.landing, name='Reports Landing'),
    path('submit_reports', views.submit_reports, name='Submit Reports'),
    path('read_unread/<slug:r_type>/<slug:r_id>', views.read_unread, name='Read Unread'),
    path('read_submit', views.read_submit, name='Read Submit'),
]
