import os

from django.shortcuts import redirect, reverse, get_object_or_404
from django.views.generic import TemplateView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.template import loader
from django.http import JsonResponse

from ..config.secrets import get_secret
from .utils import update_track_points as importer
from .utils import wp_content as wpContent
from .utils import statistic

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
            wp = wpContent.get_post_comments(trip, post_id)

        rendered_page = loader.render_to_string('maps/comments.html', {'comments': wp})
        output_data = {'html': rendered_page}

        return JsonResponse(output_data)


class CommentQty(TemplateView):
    template_name = 'maps/generate_js_message.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        trip = get_object_or_404(models.Trip, slug=self.kwargs.get('trip'))

        from django.db import transaction

        with transaction.atomic():
            _wp = wpContent.get_all_comments(trip)

            _dict = {}

            for item in _wp:
                id = item['post']

                if id in _dict:
                    _dict[id] += 1
                else:
                    _dict[id] = 1

            for post_id, qty in _dict.items():
                obj, created = models.CommentQty.objects.update_or_create(
                    trip_id=trip.pk,
                    post_id=post_id,
                    defaults={'qty': qty}
                )

        return context
