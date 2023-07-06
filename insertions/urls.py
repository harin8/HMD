from django.urls import path

from . import views

urlpatterns = [
    path('landing', views.landing, name='Insertions Landing'),
    path('create_new_forum_author',views.create_new_forum_author, name= "Create New Forum Author" ),
    path('submit_new_forum_author', views.submit_new_forum_author, name='Submit New Forum Author'),
    path('forum_author_master_list', views.forum_author_master_list, name='Forum Author Master List')
    
   
]
