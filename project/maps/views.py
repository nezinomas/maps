import datetime
import json

from django.shortcuts import render
from django.views.generic import TemplateView
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Avg, Count, Min, Sum

from wordpress import API

from ..config.secrets import get_secret
from .lib_tcx import endomondo2db as importer
from . import models


class GenerateMaps(TemplateView):
    template_name = 'maps/generate_map.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        trip = models.Trip.objects.get(pk=1)

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
                    callback=trip.blog+'/oauth1_callback'
                )

                r = wpapi.get("posts?categories={}&per_page=100".format(trip.blog_category))

                wp = json.loads(r.text)

        except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            wp['error'] = template.format(type(ex).__name__, ex.args)

        try:
            stats = models.Statistic.objects.filter(track__trip__pk=1).filter(track__date__range=(trip.start_date, trip.end_date)).filter(track__activity_type__icontains='cycling')

            total_km = stats.aggregate(Sum('total_km'))['total_km__sum']
            total_time = stats.aggregate(Sum('total_time_seconds'))['total_time_seconds__sum']
        except:
            total_km = 0.0
            total_time = 0.0

        context['st'] = {'total_km': total_km, 'total_time': total_time, 'total_days': (datetime.date.today() - trip.start_date).days}
        context['wp'] = wp
        context['trip'] = trip

        return context


def update_data(request):
    importer.main()
    context = {'message': 'ok'}

    try:
        with open('{}/js/points.js'.format(settings.STATICFILES_DIRS[0]), 'w') as the_file:
            trip = models.Trip.objects.get(pk=1)
            content = render_to_string(
                'maps/generate_js.html',
                {
                    'tracks': trip.tracks.filter(date__range=(trip.start_date, trip.end_date)).filter(activity_type__icontains='cycling')
                })
            the_file.write(content)

    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        context = {'message': template.format(type(ex).__name__, ex.args)}

    return render(request, 'maps/generate_js_message.html',context)
