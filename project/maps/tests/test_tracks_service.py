import os

import pytest
from django.conf import settings
from mock import Mock, patch

from ..factories import TripFactory
from ..utils.tracks_service import TracksService

GET_TRIP = 'project.maps.utils.tracks_service.get_trip'


def test_tracks_service_init_with_trip():
    actual = TracksService(trip=TripFactory.build())

    assert actual.trip.title == 'Trip'


@patch(GET_TRIP)
def test_tracks_service_init_without_trip(mck):
    mck.return_value = TripFactory.build()
    actual = TracksService()

    assert actual.trip.title == 'Trip'


@patch(GET_TRIP)
def test_save_data_no_trip(mck):
    mck.return_value = None
    actual = TracksService().save_data()

    assert actual == 'No trip found'


def test_tcx_file_list(fs):
    directory = os.path.join(settings.MEDIA_ROOT, 'tracks')
    fs.create_file(os.path.join(directory, '1.tcx'))
    fs.create_file(os.path.join(directory, '2.tcx'))
    fs.create_file(os.path.join(directory, '3.xxx'))


    actual = TracksService(trip=TripFactory.build()).get_files()

    assert actual == ['1', '2']
