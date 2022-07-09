from django.conf import settings
from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('project.maps.urls')),
]

if settings.DEBUG:
    import mimetypes

    import debug_toolbar
    from django.conf.urls.static import static

    mimetypes.add_type("application/javascript", ".js", True)

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    urlpatterns = [path('__debug__/', include(debug_toolbar.urls)), ] + urlpatterns
