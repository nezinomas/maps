import datetime as dt

from django.conf import settings
from django.template.loader import render_to_string

# from ..lib_tcx import endomondo2db as importer
from .. import models


def update_single_trip(trip):
    if trip.pk is not None:
        # up = importer.main(trip)
        pass

    msg = 'nothing to update'
    if up and len(up) > 0:
        _write_points_file(trip)
        msg = 'inserted {} new tracks and updated points.js file'.format(len(up))

    return msg


def recalc_single_trip(trip):
    if trip.pk is not None:
        # importer.main(trip)
        pass

    _write_points_file(trip)
    msg = 'recalculated'

    return msg


def update_all_trips():
    trips = models.Trip.objects.filter(end_date__gte=dt.date.today())

    for trip in trips:
        update_single_trip(trip)
