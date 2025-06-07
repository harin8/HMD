from django.urls import path
from .views import generate_cost_sheet

urlpatterns = [
    path('generate-cost-sheet/', generate_cost_sheet, name='generate_cost_sheet'),
] 