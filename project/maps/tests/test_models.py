import os

import pytest
from django.conf import settings

from ..factories import TripFactory
from ..models import Trip

pytestmark = pytest.mark.django_db


def test_new_trip_copy_points_file(fs):
    # create template in fake filesystem
    template = os.path.join(settings.SITE_ROOT, 'maps', 'templates', 'maps', '0-points.js')
    fs.create_file(template)

    # create fake media folder
    fs.create_dir(os.path.join(settings.MEDIA_ROOT, 'points'))

    trip = TripFactory()

    file = os.path.join(settings.MEDIA_ROOT , 'points', f'{trip.pk}-points.js')

    assert os.path.exists(file)


def test_delete_trip_deletes_points_file(fs):
    # create template in fake filesystem
    template = os.path.join(settings.SITE_ROOT, 'maps', 'templates', 'maps', '0-points.js')
    fs.create_file(template)

    # create fake media folder
    fs.create_dir(os.path.join(settings.MEDIA_ROOT, 'points'))

    trip = TripFactory()

    obj = Trip.objects.get(pk=trip.pk)
    obj.delete()

    file = os.path.join(settings.MEDIA_ROOT , 'points', f'{trip.pk}-points.js')

    assert not os.path.exists(file)
