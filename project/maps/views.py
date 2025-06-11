import re

from django.contrib.auth import logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.urls.base import reverse
from django.utils.safestring import mark_safe
from vanilla import ListView, TemplateView

from . import forms, models
from .mixins.views import (
    CreateViewMixin,
    DeleteViewMixin,
    UpdateViewMixin,
    rendered_content,
)
from .utils import views_map, wp_comments_qty, wp_content
from .utils.garmin_service import GarminService
from .utils.tracks_service import TracksService, TracksServiceData


class Trips(ListView):
    template_name = "maps/trips.html"
    model = models.Trip


class Map(TemplateView):
    template_name = "maps/map.html"

    def get_context_data(self, *args, **kwargs):
        trip_slug = self.kwargs.get("trip")
        trip = get_object_or_404(models.Trip, slug=trip_slug)

        context = views_map.base_context(trip)

        cache_key = f"geojson_{trip_slug}"
        geo_json_data = cache.get(cache_key)

        if not geo_json_data:
            tracks = (
                models.Track.objects.filter(trip=trip)
                .order_by("date")
                .select_related("stats")
            )
            geo_json_data = views_map.geo_data(tracks)
            cache_timeout = views_map.cache_timeout(trip)
            cache.set(cache_key, geo_json_data, timeout=cache_timeout)

        context["tracks"] = geo_json_data
        return super().get_context_data(*args, **kwargs) | context


class Posts(TemplateView):
    template_name = "maps/posts.html"

    def get_context_data(self, *args, **kwargs):
        trip = get_object_or_404(models.Trip, slug=self.kwargs.get("trip"))

        offset = int(self.request.GET.get("offset", 0))
        next_offset = offset + 10

        posts = None
        modula_gallery = False
        wp_error = False
        comments_qty = {}

        if (
            qs := models.CommentQty.objects.filter(trip=trip)
            .values("post_id", "qty")
            .order_by("-post_date")[offset:next_offset]
        ):
            comments_qty = {row["post_id"]: row["qty"] for row in qs}
            ids = ",".join(map(str, comments_qty.keys()))
            link = (
                f"posts?include={ids}&per_page=100&_fields=id,link,title,date,content"
            )

            try:
                posts = wp_content.get_content(link)
            except Exception:
                wp_error = "Kažkas neveikia. Bandykite prisijungti vėliau."

        if posts:
            for post in posts:
                cashed_post = post["content"]["rendered"]

                if "modula" in cashed_post:
                    modula_gallery = True
                    cashed_post = re.sub(
                        r'<a class="post-edit-link".*?</a>', "", cashed_post
                    )

                cashed_post = mark_safe(cashed_post)
                post["content"]["rendered"] = cashed_post

        context = {
            "trip": trip,
            "posts": posts,
            "comments_qty": comments_qty,
            "offset": next_offset,
            "wp_error": wp_error,
            "modula_gallery": modula_gallery,
        }

        return super().get_context_data(*args, **kwargs) | context


class Comments(TemplateView):
    template_name = "maps/comments.html"

    def get_context_data(self, **kwargs):
        post_id = self.kwargs.get("post_id")
        link = f"comments?post={post_id}&_fields=author_name,date,content"
        context = {
            "comments": wp_content.get_content(link),
        }

        return super().get_context_data(**kwargs) | context


class Login(auth_views.LoginView):
    form_class = forms.CustomAuthForm
    template_name = "maps/login.html"
    redirect_authenticated_user = True


class Logout(auth_views.LogoutView):
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        if request.user.is_authenticated:
            logout(request)
            return redirect(reverse("maps:trips"))

        return response


class Utils(LoginRequiredMixin, ListView):
    model = models.Trip
    template_name = "maps/utils.html"


class TripUpdate(LoginRequiredMixin, UpdateViewMixin):
    model = models.Trip
    form_class = forms.TripForm
    success_url = reverse_lazy("maps:utils_index")
    title = "Update Trip"

    def url(self):
        return self.object.get_absolute_url() if self.object else None


class DownloadTcx(LoginRequiredMixin, TemplateView):
    template_name = "maps/utils_messages.html"

    def get_context_data(self, *args, **kwargs):
        trip = get_object_or_404(models.Trip, slug=self.kwargs.get("trip"))

        context = {"message": GarminService(trip).get_data()}

        return super().get_context_data(*args, **kwargs) | context


class SaveNewTracks(LoginRequiredMixin, TemplateView):
    template_name = "maps/utils_messages.html"

    def get_context_data(self, *args, **kwargs):
        trip = get_object_or_404(models.Trip, slug=self.kwargs.get("trip"))

        data = TracksServiceData(trip)
        context = {"message": TracksService(data).create()}

        return super().get_context_data(*args, **kwargs) | context


class RewriteAllTracks(LoginRequiredMixin, TemplateView):
    template_name = "maps/utils_messages.html"

    def get_context_data(self, *args, **kwargs):
        trip = get_object_or_404(models.Trip, slug=self.kwargs.get("trip"))

        models.Track.objects.filter(trip=trip).delete()
        models.Statistic.objects.filter(track__trip=trip).delete()

        data = TracksServiceData(trip)
        context = {"message": TracksService(data).create_or_update()}

        return super().get_context_data(*args, **kwargs) | context


class CommentQty(LoginRequiredMixin, TemplateView):
    template_name = "maps/utils_messages.html"

    def get_context_data(self, *args, **kwargs):
        trip = get_object_or_404(models.Trip, slug=self.kwargs.get("trip"))
        wp_comments_qty.push_comments_qty(trip)

        context = {"message": ["Successfully synced with wordpress blog"]}

        return super().get_context_data(*args, **kwargs) | context
