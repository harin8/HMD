from django.urls import path

from . import views

urlpatterns = [
    path('', views.landing, name='Certificates Landing'),
    path('submit_certificate/', views.submit_certificate, name='Submit Certificate'),
    path('further_cert_info/<slug:id>', views.further_cert_info, name='Further Cert Info'),
    path('further_cert_submit/', views.further_cert_submit, name='Further Cert Submit'),
]
