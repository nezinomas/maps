import os
import re

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.utils.safestring import mark_safe
from django.views.generic import ListView, TemplateView

from . import models, utils
from .utils.garmin_service import GarminService
from .utils.points_service import PointsService
from .utils.tracks_service import TracksService


class Trips(ListView):
    model = models.Trip


class Map(TemplateView):
    template_name = "maps/map.html"

    def get_context_data(self, *args, **kwargs):
        trip = get_object_or_404(models.Trip, slug=self.kwargs.get("trip"))

        self.kwargs["trip_from_maps_view"] = trip
        points_file = os.path.join(
            settings.MEDIA_ROOT, "points", f"{trip.pk}-points.js"
        )
        context = {
            "trip": trip,
            "statistic": utils.statistic_service.get_statistic(trip),
            "google_api_key": settings.ENV("GOOGLE_API_KEY"),
            "js_version": os.path.getmtime(points_file),
        }

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
                posts = utils.wp.get_json(trip.blog, link)
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
        trip = get_object_or_404(models.Trip, slug=self.kwargs.get("trip"))
        post_id = self.kwargs.get("post_id")
        link = f"comments?post={post_id}&_fields=author_name,date,content"
        context = {
            "comments": utils.wp_content.get_json(trip.blog, link),
        }

        return super().get_context_data(**kwargs) | context


class Utils(LoginRequiredMixin, TemplateView):
    login_url = "/admin/"
    template_name = "maps/utils.html"

    def get_context_data(self, **kwargs):
        context = {
            "slug": self.kwargs.get("trip"),
        }
        return super().get_context_data(**kwargs) | context


class DownloadTcx(LoginRequiredMixin, TemplateView):
    login_url = "/admin/"
    template_name = "maps/utils_messages.html"

    def get_context_data(self, *args, **kwargs):
        trip = get_object_or_404(models.Trip, slug=self.kwargs.get("trip"))

        context = {"message": GarminService(trip).get_data()}

        return super().get_context_data(*args, **kwargs) | context


class SaveNewTracks(LoginRequiredMixin, TemplateView):
    login_url = "/admin/"
    template_name = "maps/utils_messages.html"

    def get_context_data(self, *args, **kwargs):
        trip = get_object_or_404(models.Trip, slug=self.kwargs.get("trip"))

        context = {"message": TracksService(trip).save_data()}

        return super().get_context_data(*args, **kwargs) | context


class RewriteAllTracks(LoginRequiredMixin, TemplateView):
    login_url = "/admin/"
    template_name = "maps/utils_messages.html"

    def get_context_data(self, *args, **kwargs):
        trip = get_object_or_404(models.Trip, slug=self.kwargs.get("trip"))

        models.Track.objects.filter(trip=trip).delete()
        models.Statistic.objects.filter(track__trip=trip).delete()

        context = {"message": TracksService(trip).save_data()}

        return super().get_context_data(*args, **kwargs) | context


class SaveNewPoints(LoginRequiredMixin, TemplateView):
    login_url = "/admin/"
    template_name = "maps/utils_messages.html"

    def get_context_data(self, *args, **kwargs):
        trip = get_object_or_404(models.Trip, slug=self.kwargs.get("trip"))

        context = {"message": PointsService(trip).update_points()}

        return super().get_context_data(*args, **kwargs) | context


class RewriteAllPoints(LoginRequiredMixin, TemplateView):
    login_url = "/admin/"
    template_name = "maps/utils_messages.html"

    def get_context_data(self, *args, **kwargs):
        trip = get_object_or_404(models.Trip, slug=self.kwargs.get("trip"))

        context = {"message": PointsService(trip).update_all_points()}

        return super().get_context_data(*args, **kwargs) | context


class RegeneratePointsFile(LoginRequiredMixin, TemplateView):
    login_url = "/admin/"
    template_name = "maps/utils_messages.html"

    def get_context_data(self, *args, **kwargs):
        trip = get_object_or_404(models.Trip, slug=self.kwargs.get("trip"))

        context = {"message": PointsService(trip).regenerate_points_file()}

        return super().get_context_data(*args, **kwargs) | context


class CommentQty(LoginRequiredMixin, TemplateView):
    template_name = "maps/utils_messages.html"

    def get_context_data(self, *args, **kwargs):
        trip = get_object_or_404(models.Trip, slug=self.kwargs.get("trip"))
        utils.wp_comments_qty.push_comments_qty(trip)

        context = {"message": ["done"]}

        return super().get_context_data(*args, **kwargs) | context
