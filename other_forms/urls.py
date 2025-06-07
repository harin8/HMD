from django.urls import path, re_path
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path('', views.landing, name='Other Forms Landing'),
    path('submit_other_forms/', views.submit_certificate, name='Submit Other Forms'),
    path('further_other_forms_info/<slug:id>', views.further_other_forms_info, name='Further Other Forms Info'),
    path('further_other_forms_submit/', views.further_other_forms_submit, name='Further Other Forms Submit'),
    path('submit_other_forms_File', views.submit_otherform_File, name='Further Other Forms File Submit'),
    path('pdf_view_other_forms/<slug:id>', views.pdf_view, name='PDF View Other Forms'),
    re_path(r'^view-pdf/$', views.pdf_view, name='pdf_view_judgments'),
    path('delete_other_forms/', views.delete_other_forms, name='Delete Other Forms'),
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
