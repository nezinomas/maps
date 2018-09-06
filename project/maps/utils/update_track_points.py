from django.conf import settings
from django.template.loader import render_to_string

from ..lib_tcx import endomondo2db as importer
from .. import models


def update_track_points():
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

    return context
