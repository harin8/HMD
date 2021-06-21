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
    path('edit_party_list', views.edit_party_list, name='Edit Party List'),
    path('edit_party/<slug:id>', views.edit_party, name='Edit One Party'),
    path('submit_edit_party', views.submit_edit_party, name='Submit Edit Party')
]
