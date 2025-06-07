from django.urls import path, re_path
from django.conf.urls.static import static
from django.conf import settings

from . import views

urlpatterns = [
    path('', views.landing, name='Judgments Landing'),
    path('submit_judgments', views.submit_judgments, name='Submit Judgments'),
    path('further_judg_info/<slug:id>', views.further_judg_info, name='Further Judg Info'),
    path('submit_judg_summaries', views.submit_judg_summaries, name='Further Judg Summary Submit'),
    path('submit_judg_Citation', views.submit_judg_Citation, name='Further Judg Citation Submit'),
    path('submit_judg_File', views.submit_judg_File, name='Further Judg File Submit'),
    path('summary_landing/<slug:id>', views.summary_landing, name='Summary Landing'),
    path('pdf_view_judgments/<slug:id>', views.pdf_view, name='PDF View Judgments'),
    re_path(r'^view-pdf/$', views.pdf_view, name='pdf_view_judgments')
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
