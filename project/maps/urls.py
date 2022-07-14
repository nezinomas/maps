from django.urls import path

from . import views

app_name = 'maps'

urlpatterns = [
    path('', views.index, name='first'),
    path('<slug:trip>/', views.GenerateMaps.as_view(), name='index'),
    path('<slug:trip>/utils/', views.Utils.as_view(), name='utils'),
    path('<slug:trip>/download_tcx/', views.DownloadTcx.as_view(), name='download_tcx'),
    path('<slug:trip>/update_tracks/', views.UpdateTracks.as_view(), name='update_tracks'),
    path('<slug:trip>/update_all_tracks/', views.UpdateAllTracks.as_view(), name='update_all_tracks'),
    path('<slug:trip>/update_points/', views.UpdatePoints.as_view(), name='update_points'),
    path('<slug:trip>/update_all_points/', views.UpdateAllPoints.as_view(), name='update_all_points'),
    path('<slug:trip>/qty/', views.CommentQty.as_view(), name='comment_qty'),
    path('<slug:trip>/<slug:post>/comments/', views.Comments.as_view(), name='comments'),
]
