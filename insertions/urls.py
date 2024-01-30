from django.urls import path

from . import views

urlpatterns = [
    path('landing', views.landing, name='Insertions Landing'),
    path('create_new_forum_author', views.create_new_forum_author, name="Create New Forum Author"),
    path('submit_new_forum_author', views.submit_new_forum_author, name='Submit New Forum Author'),
    path('forum_author_master_list', views.forum_author_master_list, name='Forum Author Master List'),
    path('create_new_certificate_description', views.create_new_certificate_description,
         name="Create New Certificate Description"),
    path('submit_new_certificate_description', views.submit_new_certificate_description,
         name='Submit New Certificate Description'),
    path('certificate_description_master_list', views.certificate_description_master_list,
         name='Certificate Description Master List'),
    path('delete_certificate_description/<slug:p_no>', views.delete_certificate_description,
         name='Delete Certificate Description'),
    path('create_new_other_form_description', views.create_new_other_form_description,
         name="Create New Other Form Description"),
    path('submit_new_other_form_description', views.submit_new_other_form_description,
         name='Submit New Other Form Description'),
    path('other_form_description_master_list', views.other_form_description_master_list,
         name='Other Form Description Master List'),
    path('delete_other_form_description/<slug:p_no>', views.delete_other_form_description,
         name='Delete Other Form Description'),
    path('create_new_proceedings_description', views.create_new_proceedings_description,
         name="Create New Proceedings Description"),
    path('submit_new_proceedings_description', views.submit_new_proceedings_description,
         name='Submit New Proceedings Description'),
    path('proceedings_description_master_list', views.proceedings_description_master_list,
         name='Proceedings Description Master List'),
    path('delete_proceedings_description/<slug:p_no>/<str:p_type>', views.delete_proceedings_description,
         name='Delete Proceedings Description')

]
