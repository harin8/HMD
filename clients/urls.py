from django.urls import path

from . import views

urlpatterns = [
    path('client_landing', views.client_landing, name='Client Landing'),
    path('client_master_list', views.client_master_list, name='Client Master List'),
    path('create_new_client', views.create_new_client, name='Create New Client'),
    path('submit_new_client', views.submit_new_client, name='Submit New Client')
]
