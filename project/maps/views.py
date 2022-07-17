import os

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.template import loader
from django.views.generic import ListView, TemplateView

from . import models
from .utils import statistic_service
from .utils import wp_comments_qty as wpQty
from .utils import wp_content as wpContent
from .utils.garmin_service import GarminService
from .utils.points_service import PointsService
from .utils.tracks_service import TracksService


class Trips(ListView):
    model = models.Trip


class Map(TemplateView):
    template_name = 'maps/map.html'

    def get_context_data(self, *args, **kwargs):
        wp = None
        wp_error = False
        comments = None

        trip = get_object_or_404(models.Trip, slug=self.kwargs.get('trip'))

        try:
            if trip.blog:
                wp = wpContent.get_posts(trip)
                comments = wpContent.get_comment_qty(trip)

        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            wp_error = template.format(type(ex).__name__, ex.args)

        context = {
            'wp': wp,
            'wp_error': wp_error,
            'trip': trip,
            'qty': comments,
            'st': statistic_service.get_statistic(trip),
            'google_api_key': settings.ENV("GOOGLE_API_KEY"),
            'js_version': os.path.getmtime(
                f'{settings.MEDIA_ROOT}/points/{trip.pk}-points.js'),
        }

        return super().get_context_data(*args, **kwargs) | context


class Comments(TemplateView):
    template_name = 'maps/comments.html'

    def get_context_data(self, **kwargs):
        trip = get_object_or_404(models.Trip, slug=self.kwargs.get('trip'))
        post_id = self.kwargs.get('post_id')
        wp = wpContent.get_comments(trip, post_id)
        context = {
            'comments': wp
        }

        return super().get_context_data(**kwargs) | context


class Utils(LoginRequiredMixin, TemplateView):
    login_url = '/admin/'
    template_name = 'maps/utils.html'

    def get_context_data(self, **kwargs):
        context = {
            'slug': self.kwargs.get('trip'),
        }
        return super().get_context_data(**kwargs) | context


class DownloadTcx(LoginRequiredMixin, TemplateView):
    login_url = '/admin/'
    template_name = 'maps/utils_messages.html'

    def get_context_data(self, *args, **kwargs):
        trip = get_object_or_404(models.Trip, slug=self.kwargs.get('trip'))

        context = {'message': GarminService(trip).get_data()}

        return super().get_context_data(*args, **kwargs) | context


class SaveNewTracks(LoginRequiredMixin, TemplateView):
    login_url = '/admin/'
    template_name = 'maps/utils_messages.html'

    def get_context_data(self, *args, **kwargs):
        trip = get_object_or_404(models.Trip, slug=self.kwargs.get('trip'))

        context = {'message': TracksService(trip).save_data() }

        return super().get_context_data(*args, **kwargs) | context


class RewriteAllTracks(LoginRequiredMixin, TemplateView):
    login_url = '/admin/'
    template_name = 'maps/utils_messages.html'

    def get_context_data(self, *args, **kwargs):
        trip = get_object_or_404(models.Trip, slug=self.kwargs.get('trip'))

        models.Track.objects.filter(trip=trip).delete()
        models.Statistic.objects.filter(track__trip=trip).delete()

        context = {'message': TracksService(trip).save_data() }

        return super().get_context_data(*args, **kwargs) | context


class SaveNewPoints(LoginRequiredMixin, TemplateView):
    login_url = '/admin/'
    template_name = 'maps/utils_messages.html'

    def get_context_data(self, *args, **kwargs):
        trip = get_object_or_404(models.Trip, slug=self.kwargs.get('trip'))

        context = {'message': PointsService(trip).update_points() }

        return super().get_context_data(*args, **kwargs) | context


class RewriteAllPoints(LoginRequiredMixin, TemplateView):
    login_url = '/admin/'
    template_name = 'maps/utils_messages.html'

    def get_context_data(self, *args, **kwargs):
        trip = get_object_or_404(models.Trip, slug=self.kwargs.get('trip'))

        context = {'message': PointsService(trip).update_all_points() }

        return super().get_context_data(*args, **kwargs) | context

class CommentQty(LoginRequiredMixin, TemplateView):
    template_name = 'maps/utils_messages.html'

    def get_context_data(self, *args, **kwargs):
        trip = get_object_or_404(models.Trip, slug=self.kwargs.get('trip'))
        wpQty.push_post_comment_qty(trip)

        context = {'message': 'done' }

        return super().get_context_data(*args, **kwargs) | context
