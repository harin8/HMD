from django.urls import path
from . import views

urlpatterns = [
    path('', views.accounts_landing, name='accounts_landing'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('users/', views.user_management, name='user_management'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('permission-denied/', views.permission_denied, name='permission_denied'),
]