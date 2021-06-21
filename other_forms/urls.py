from django.urls import path

from . import views

urlpatterns = [
    path('', views.landing, name='Other Forms Landing'),
    path('submit_other_forms/', views.submit_certificate, name='Submit Other Forms'),
    path('further_other_forms_info/<slug:id>', views.further_other_forms_info, name='Further Other Forms Info'),
    path('further_other_forms_submit/', views.further_other_forms_submit, name='Further Other Forms Submit')
]
