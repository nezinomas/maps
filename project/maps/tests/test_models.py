import os

import pytest
from django.conf import settings

from ..factories import TripFactory
from ..models import Trip

pytestmark = pytest.mark.django_db


def test_new_trip_copy_points_file(project_fs):
    trip = TripFactory()

    file = os.path.join(settings.MEDIA_ROOT , 'points', f'{trip.pk}-points.js')

    assert os.path.exists(file)


def test_delete_trip_deletes_points_file(project_fs):
    trip = TripFactory()

    obj = Trip.objects.get(pk=trip.pk)
    obj.delete()

    file = os.path.join(settings.MEDIA_ROOT , 'points', f'{trip.pk}-points.js')

    assert not os.path.exists(file)
