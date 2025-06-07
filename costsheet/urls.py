from django.urls import path
from . import views

urlpatterns = [
    path('generate_cost_sheet/', views.generate_cost_sheet, name='generate_cost_sheet'),
] 