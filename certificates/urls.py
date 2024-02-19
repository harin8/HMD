from django.urls import path
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path('', views.landing, name='Certificates Landing'),
    path('submit_certificate/', views.submit_certificate, name='Submit Certificate'),
    path('further_cert_info/<slug:id>', views.further_cert_info, name='Further Cert Info'),
    path('further_cert_submit/', views.further_cert_submit, name='Further Cert Submit'),
    path('submit_cert_File', views.submit_cert_File, name='Further Cert File Submit'),
    path('pdf_view_certificates/<slug:id>', views.pdf_view, name='PDF View Certificates'),
    url(r'^view-pdf/$', views.pdf_view, name='pdf_view_judgments')
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)