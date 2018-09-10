import datetime
import json

from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.generic import TemplateView
from django.db.models import Sum
from django.contrib.auth.mixins import LoginRequiredMixin

from wordpress import API

from ..config.secrets import get_secret
from .utils import update_track_points as importer
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
        wp = {}

        try:
            if trip.blog:
                wpapi = API(
                    url=trip.blog,
                    consumer_key=get_secret("CONSUMER_KEY"),
                    consumer_secret=get_secret("CONSUMER_SECRET"),
                    api="wp-json",
                    version="wp/v2",
                    wp_user=get_secret("WP_USER"),
                    wp_pass=get_secret("WP_PASS"),
                    oauth1a_3leg=True,
                    creds_store="",
                    callback='{}/oauth1_callback'.format(trip.blog)
                )

                r = wpapi.get("posts?categories={}&per_page=100".format(trip.blog_category))

                wp = json.loads(r.text)

        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            wp['error'] = template.format(type(ex).__name__, ex.args)

        try:
            stats = models.Statistic.objects.filter(track__trip__pk=trip.pk).filter(track__date__range=(trip.start_date, trip.end_date)).filter(track__activity_type__icontains='cycling')

            total_km = stats.aggregate(Sum('total_km'))['total_km__sum']
            total_time = stats.aggregate(Sum('total_time_seconds'))['total_time_seconds__sum']
        except:
            total_km = 0.0
            total_time = 0.0

        context['st'] = {'total_km': total_km, 'total_time': total_time, 'total_days': ((datetime.date.today() - trip.start_date).days)+1}
        context['wp'] = wp
        context['trip'] = trip
        context['google_api_key'] = get_secret("GOOGLE_API_KEY")

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
