from django.conf import settings
from django.conf.urls import static
from django.urls import path

from . import views

app_name = 'maps'

urlpatterns = [
    path('', views.GenerateMaps.as_view(), name='index'),
    path('up/', views.UpdateMaps.as_view(), name='update')
]

if settings.DEBUG:
    from django.views.defaults import server_error, page_not_found, permission_denied

    urlpatterns += [
        path('403/', permission_denied, kwargs={'exception': Exception("Permission Denied")}, name='error403'),
        path('404/', page_not_found, kwargs={'exception': Exception("Page not Found")}, name='error404'),
        path('500/', server_error, name='error500'),
    ]
    urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
