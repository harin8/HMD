from django.urls import path, re_path
from django.conf.urls.static import static
from django.conf import settings

from . import views

urlpatterns = [
    path('other_proceedings_landing', views.landing, name='Other Proceedings Landing'),
    path('judicial_proceedings_landing/', views.judicial_proceedings_landing, name='Judicial Proceedings Landing'),
    path('regular_proceedings_landing/', views.regular_proceedings_landing, name='Regular Proceedings Landing'),
    path('submit_proceedings/', views.submit_proceedings, name='Submit Proceedings'),
    path('submit_judicial_proceedings/', views.submit_judicial_proceedings, name='Submit Judicial Proceedings'),
    path('submit_regular_proceedings/', views.submit_regular_proceedings, name='Submit Regular Proceedings'),
    path('further_proc_info/<slug:id>', views.further_proc_info, name='Further Proc Info'),
    path('event_landing/<slug:id>', views.event_landing, name='Event Landing'),
    path('pdf_view/<slug:id>', views.pdf_view, name='PDF View'),
    path('further_pro_submit/', views.further_proc_submit, name='Further Proc Submit'),
    path('submit_proceedings_events/', views.submit_proceedings_events, name='Further Proc Event Submit'),
    re_path(r'^view-pdf/$', views.pdf_view, name='pdf_view'),
    path('mark-case/', views.mark_case, name='Mark Case'),
    path('delete-proceedings/', views.delete_proceedings, name='Delete Proceedings'),
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
