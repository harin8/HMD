from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', include('IT_Return.urls')), 
    path('accounts/', include('accounts.urls')),
    path('certificates/', include('certificates.urls')),
    path('admin/', admin.site.urls),
    path('clients/', include('clients.urls')),
    path('contacts/', include('contacts.urls')),
    path('other_forms/', include('other_forms.urls')),
    path('reports/', include('reports.urls')),
    path('tds/', include('tds.urls')),
    path('proceedings/', include('proceedings.urls')), 
    path('judgments/', include('judgments.urls')),
    path('insertions/', include('insertions.urls')),
    path('timesheet/', include('timesheet.urls')),
    path('costsheet/', include('costsheet.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
