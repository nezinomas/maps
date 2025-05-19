from django.urls import path

from . import views

app_name = "maps"

urlpatterns = [
    path("", views.Trips.as_view(), name="trips"),
    path("<slug:trip>/", views.Map.as_view(), name="index"),
    path("<slug:trip>/posts/", views.Posts.as_view(), name="posts"),
    path("<slug:trip>/utils/", views.Utils.as_view(), name="utils"),
    path("<slug:trip>/download_tcx/", views.DownloadTcx.as_view(), name="download_tcx"),
    path(
        "<slug:trip>/update_tracks/",
        views.SaveNewTracks.as_view(),
        name="update_tracks",
    ),
    path(
        "<slug:trip>/update_all_tracks/",
        views.RewriteAllTracks.as_view(),
        name="update_all_tracks",
    ),
    path(
        "<slug:trip>/update_points/",
        views.SaveNewPoints.as_view(),
        name="update_points",
    ),
    path(
        "<slug:trip>/regenerate_points_file/",
        views.RegeneratePointsFile.as_view(),
        name="regenerate_points_file",
    ),
    path(
        "<slug:trip>/update_all_points/",
        views.RewriteAllPoints.as_view(),
        name="update_all_points",
    ),
    path("<slug:trip>/qty/", views.CommentQty.as_view(), name="comment_qty"),
    path(
        "<slug:trip>/<int:post_id>/comments/", views.Comments.as_view(), name="comments"
    ),
]
