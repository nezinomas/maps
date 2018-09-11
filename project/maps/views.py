import datetime
import os

from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.generic import TemplateView
from django.db.models import Sum
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.template import loader
from django.http import JsonResponse

from ..config.secrets import get_secret
from .utils import update_track_points as importer
from .utils import wp_content as wpContent

from . import models


def index(request):
    queryset = models.Trip.objects.all().order_by('-pk')[:1]
    content = get_object_or_404(queryset)
    return redirect(
        reverse(
            'maps:index',
            kwargs={'trip': content.slug}
        )
    )


class GenerateMaps(TemplateView):
    template_name = 'maps/generate_map.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        trip = get_object_or_404(models.Trip, slug=self.kwargs.get('trip'))
        wp_error = False
        wp = None
        try:
            if trip.blog:
                wp = wpContent.get_content(
                    trip.blog,
                    "posts?categories={}&per_page=70".format(
                        trip.blog_category)
                )

        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            wp_error = template.format(type(ex).__name__, ex.args)

        try:
            stats = models.Statistic.objects.filter(track__trip__pk=trip.pk).filter(track__date__range=(trip.start_date, trip.end_date)).filter(track__activity_type__icontains='cycling')

            total_km = stats.aggregate(Sum('total_km'))['total_km__sum']
            total_time = stats.aggregate(Sum('total_time_seconds'))['total_time_seconds__sum']
            total_ascent = stats.aggregate(Sum('ascent'))['ascent__sum']
            total_descent = stats.aggregate(Sum('descent'))['descent__sum']
        except:
            total_km = 0.0
            total_time = 0.0

        context['st'] = {
            'total_km': total_km,
            'total_time': total_time,
            'total_days': ((datetime.date.today() - trip.start_date).days)+1,
            'total_ascent': total_ascent,
            'total_descent': total_descent,
        }
        context['wp'] = wp
        context['wp_error'] = wp_error
        context['trip'] = trip
        context['google_api_key'] = get_secret("GOOGLE_API_KEY")
        context['js_version'] = os.path.getmtime('{}/points/{}-points.js'.format(settings.MEDIA_ROOT, trip.pk))

        return context


class UpdateMaps(LoginRequiredMixin, TemplateView):
    login_url = '/admin/'
    template_name = 'maps/generate_js_message.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        trip = get_object_or_404(models.Trip, slug=self.kwargs.get('trip'))

        context['message'] = importer.update_single_trip(trip)

        return context


class RecalcMaps(LoginRequiredMixin, TemplateView):
    login_url = '/admin/'
    template_name = 'maps/generate_js_message.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        trip = get_object_or_404(models.Trip, slug=self.kwargs.get('trip'))

        context['message'] = importer.recalc_single_trip(trip)

        return context


class Comments(TemplateView):

    def get(self, request, *args, **kwargs):
        post_id = request.GET.get('post_id', False)
        get_remote = request.GET.get('get_remote', False)

        wp = []
        if get_remote == 'true':
            trip = get_object_or_404(models.Trip, slug=self.kwargs.get('trip'))
            wp = wpContent.get_content(
                trip.blog,
                "comments?post={}&per_page=50".format(post_id)
            )

        rendered_page = loader.render_to_string('maps/comments.html', {'comments': wp})
        output_data = {'html': rendered_page }

        return JsonResponse(output_data)
