from django.urls import path

from . import views

urlpatterns = [
    path('client_landing', views.client_landing, name='Client Landing'),
    path('client_master_list', views.client_master_list, name='Client Master List'),
    path('create_new_client', views.create_new_client, name='Create New Client'),
    path('submit_new_client', views.submit_new_client, name='Submit New Client'),
    path('party_master_list', views.party_master_list, name='Party Master List'),
    path('create_new_party', views.create_new_party, name='Create New Party'),
    path('submit_new_party', views.submit_new_party, name='Submit New Party'),
    path('close_party_list', views.close_party_list, name='Close Party List'),
    path('close_party/<slug:id>', views.close_party, name='Close One Party'),
    path('submit_close_party', views.submit_close_party, name='Submit Close Party'),
    path('group_master_list', views.group_master_list, name='Group Master List'),
    path('create_new_group', views.create_new_group, name='Create New Group'),
    path('submit_new_group', views.submit_new_group, name='Submit New Group'),
    path('close_group_list', views.close_group_list, name='Close Group List'),
    path('close_one_group', views.close_one_group, name='Close One Group'),
    path('transfer_party_list', views.transfer_party_list, name='Transfer Party List'),
    path('transfer_party/<slug:id>', views.transfer_party, name='Transfer One Party'),
    path('submit_transfer_party', views.submit_transfer_party, name='Submit Transfer Party'),
    path('new_client_code', views.new_client_code, name='New Client Code'),
    path('password_validate', views.password_validate, name='Password Validate')
]
