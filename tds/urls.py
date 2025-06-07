from django.urls import path

from . import views

urlpatterns = [
    path('', views.tds_landing, name='TDS Landing'),
    path('create_new_tds/<slug:client_no>/<slug:ay>/<slug:quarter>/<slug:form>/<slug:type>', views.create_new_tds,
         name='Create New TDS'),
    path('submit_new_tds/', views.submit_new_tds, name='Submit New TDS'),
    path('existing_tds_list', views.existing_tds_list, name='Existing TDS List'),
    path('further_tds_info/<slug:client_no>/<slug:ay>/<slug:quarter>/<slug:form>/<slug:type>', views.further_tds_info,
         name='Further TDS Info'),
    path('further_tds_submit', views.further_tds_submit, name='Further TDS Submit'),
    path('delete_tds', views.delete_tds, name='Delete TDS'),
]
