from django.urls import path

from . import views

app_name = "maps"

urlpatterns = [
    path("", views.Trips.as_view(), name="trips"),
    path("utils/", views.Utils.as_view(), name="utils_index"),
    path("utils/login/", views.Login.as_view(), name="login"),
    path("utils/logout/", views.Logout.as_view(), name="logout"),
    path(
        "utils/create/",
        views.TripCreate.as_view(),
        name="create_trip"
    ),
    path(
        "utils/update/<int:pk>/",
        views.TripUpdate.as_view(),
        name="update_trip"
    ),
    path(
        "utils/trip_list/",
        views.TripList.as_view(),
        name="list_trips"
    ),
    path(
        "utils/download_tcx/<slug:trip>/",
        views.DownloadTcx.as_view(),
        name="download_tcx",
    ),
    path(
        "utils/tcx_date/<slug:trip>/",
        views.GetTcxByDate.as_view(),
        name="tcx_date",
    ),
    path(
        "utils/update_tracks/<slug:trip>/",
        views.SaveNewTracks.as_view(),
        name="update_tracks",
    ),
    path(
        "utils/update_all_tracks/<slug:trip>/",
        views.RewriteAllTracks.as_view(),
        name="update_all_tracks",
    ),
    path("<slug:trip>/", views.Map.as_view(), name="index"),
    path("<slug:trip>/posts/", views.Posts.as_view(), name="posts"),
    path("<slug:trip>/qty/", views.CommentQty.as_view(), name="comment_qty"),
    path(
        "<slug:trip>/<int:post_id>/comments/", views.Comments.as_view(), name="comments"
    ),
]
