from django.urls import path

from . import views

urlpatterns = [
    path('', views.landing, name='Landing'),
    path('new_it_return', views.new_it_return, name='New IT Return'),
    path('create_new_return/<slug:it_no>/<slug:ay>/<slug:r_type>', views.create_new_return, name='Create New Return'),
    path('submit_new_return', views.submit_new_return, name='Submit New Return'),
    path('further_return_info/<slug:it_no>/<slug:ay>/<slug:r_type>', views.further_return_info, name='Further Return '
                                                                                                    'Info'),
    path('further_return_submit', views.further_return_submit, name='Further Return Submit'),
    path('existing_return_list', views.existing_return_list, name='Existing Return List'),
    path('cpc_list', views.cpc_list, name='CPC List'),
    path('further_cpc_info/<slug:it_no>/<slug:ay>/<slug:r_type>', views.further_cpc_info, name='Further CPC Info'),
    path('further_cpc_submit', views.further_cpc_submit, name='Further CPC Submit'),
    path('group_filter_list', views.group_filter_list, name='Group Filter List')

]
