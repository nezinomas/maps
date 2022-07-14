import os

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, reverse
from django.template import loader
from django.views.generic import TemplateView

from . import models
from .utils import statistic
from .utils import wp_comments_qty as wpQty
from .utils import wp_content as wpContent
from .utils.garmin_service import GarminService
from .utils.points_service import PointsService
from .utils.tracks_service import TracksService


def index(request):
    queryset = models.Trip.objects.all().order_by('-pk')[:1]
    content = get_object_or_404(queryset)
    return redirect(
        reverse(
            'maps:index',
            kwargs={'trip': content.slug}
        )
    )


class Utils(LoginRequiredMixin, TemplateView):
    login_url = '/admin/'
    template_name = 'maps/utils.html'

    def get_context_data(self, **kwargs):
        trip = get_object_or_404(models.Trip, slug=self.kwargs.get('trip'))
        points = models.Point.objects.filter(track__trip=trip).values_list('latitude', 'longitude')
        print(f'points:\n{points}')
        context = {
            'slug': self.kwargs.get('trip'),
        }
        return super().get_context_data(**kwargs) | context


class GenerateMaps(TemplateView):
    template_name = 'maps/generate_map.html'

    def get_context_data(self, *args, **kwargs):
        wp = None
        wp_error = False
        comments = None

        context = super().get_context_data(*args, **kwargs)
        trip = get_object_or_404(models.Trip, slug=self.kwargs.get('trip'))

        try:
            if trip.blog:
                wp = wpContent.get_posts(trip)
                comments = wpContent.get_comment_qty(trip)

        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            wp_error = template.format(type(ex).__name__, ex.args)

        context['wp'] = wp
        context['wp_error'] = wp_error
        context['trip'] = trip
        context['qty'] = comments
        context['st'] = statistic.get_statistic(trip)
        context['google_api_key'] = settings.ENV("GOOGLE_API_KEY")
        context['js_version'] = os.path.getmtime('{}/points/{}-points.js'.format(settings.MEDIA_ROOT, trip.pk))

        return context


class DownloadTcx(LoginRequiredMixin, TemplateView):
    login_url = '/admin/'
    template_name = 'maps/generate_js_message.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        trip = get_object_or_404(models.Trip, slug=self.kwargs.get('trip'))

        context['message'] = GarminService(trip).get_data()

        return context


class SaveNewTracks(LoginRequiredMixin, TemplateView):
    login_url = '/admin/'
    template_name = 'maps/generate_js_message.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        trip = get_object_or_404(models.Trip, slug=self.kwargs.get('trip'))

        context['message'] = TracksService(trip).save_data()

        return context


class RewriteAllTracks(LoginRequiredMixin, TemplateView):
    login_url = '/admin/'
    template_name = 'maps/generate_js_message.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        trip = get_object_or_404(models.Trip, slug=self.kwargs.get('trip'))

        models.Track.objects.filter(trip=trip).delete()
        models.Statistic.objects.filter(track__trip=trip).delete()

        context['message'] = TracksService(trip).save_data()

        return context


class SaveNewPoints(LoginRequiredMixin, TemplateView):
    login_url = '/admin/'
    template_name = 'maps/generate_js_message.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        trip = get_object_or_404(models.Trip, slug=self.kwargs.get('trip'))

        context['message'] = PointsService(trip).update_points()

        return context


class RewriteAllPoints(LoginRequiredMixin, TemplateView):
    login_url = '/admin/'
    template_name = 'maps/generate_js_message.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        trip = get_object_or_404(models.Trip, slug=self.kwargs.get('trip'))

        context['message'] = PointsService(trip).update_all_points()

        return context


class Comments(TemplateView):
    def get(self, request, *args, **kwargs):
        post_id = request.GET.get('post_id', False)
        get_remote = request.GET.get('get_remote', False)

        wp = []
        if get_remote == 'true':
            trip = get_object_or_404(models.Trip, slug=self.kwargs.get('trip'))
            wp = wpContent.get_comments(trip, post_id)

        rendered_page = loader.render_to_string('maps/comments.html', {'comments': wp})
        output_data = {'html': rendered_page}

        return JsonResponse(output_data)


class CommentQty(TemplateView):
    template_name = 'maps/generate_js_message.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        trip = get_object_or_404(models.Trip, slug=self.kwargs.get('trip'))

        wpQty.push_post_comment_qty(trip)

        context['message'] = 'done'

        return context
