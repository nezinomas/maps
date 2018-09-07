import datetime as dt

from django.conf import settings
from django.template.loader import render_to_string

from ..lib_tcx import endomondo2db as importer
from .. import models


def new_pk(instance):
    if not instance.pk:
        model = instance.__class__
        try:
            new_id = model.objects.latest('pk').pk
            if new_id:
                new_id += 1
            else:
                new_id = 1
        except:
            new_id = 1
    else:
        new_id = instance.pk

    return new_id


def update_track_points(trip):

    if not trip:
        return

    tracks = ''
    get_data = True
    pk = trip.pk

    if trip.pk is not None:
        tracks = trip.tracks.filter(date__range=(trip.start_date, trip.end_date)).filter(
            activity_type__icontains='cycling')
    else:
        pk = new_pk(trip)
        get_data = False

    if tracks.count() <= 0:
        get_data = False

    with open('{}/points/{}-points.js'.format(settings.MEDIA_ROOT, pk), 'w') as the_file:
        content = render_to_string('maps/generate_js.html', {'tracks': tracks, 'get_data': get_data})
        the_file.write(content)


def update_single_trip(trip):
    if trip.pk is not None:
        up = importer.main()

    context = {'message': 'nothing to update'}
    if up and len(up) > 0:
        update_track_points(trip)
        context = {'message': 'inserted {} new tracks and updated points.js file'.format(len(up))}

    return context


def update_all_trips():
    up = importer.main()

    if up and len(up) > 0:
        trips = models.Trip.objects.filter(end_date__gte=dt.date.today())

        for trip in trips:
            update_track_points(trip)
