from django.urls import path

from . import views

urlpatterns = [
    path('landing', views.landing, name='Contacts Landing'),
    path('create_new_contact', views.create_new_contact, name='Create New Contact'),
    path('submit_new_contact', views.submit_new_contact, name='Submit New Contact'),
    path('edit_contacts', views.edit_contacts, name='Edit Contacts'),
    path('contact_master_list', views.contact_master_list, name='Contact Master List'),
    path('edit_contact/<slug:id>', views.edit_contact, name='Edit One Contact'),
    path('submit_edit_contact', views.submit_edit_contact, name='Submit Edit Contact')
]
