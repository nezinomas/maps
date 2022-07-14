import os
from datetime import datetime, timezone

import pytest
from django.conf import settings
from mock import patch

from ..factories import TrackFactory, TripFactory
from ..models import Statistic, Track
from ..utils.tracks_service import TracksService

TRACKS_SERVICE = 'project.maps.utils.tracks_service.TracksService'
GET_TRIP = 'project.maps.utils.tracks_service.get_trip'

pytestmark = pytest.mark.django_db


@pytest.fixture
def _activity():
    activity = {
        'start_time': '2022-01-01 03:02:01 +0000',
        'total_km': 12.345,
        'total_time_seconds': 1918.1,
        'avg_speed': 23.40,
        'max_speed': 47.52,
        'calories': 33.0,
        'avg_cadence': None,
        'avg_heart': None,
        'max_heart': None,
        'avg_temperature': None,
        'ascent': 111.0,
        'descent': 222.0,
        'min_altitude': 5,
        'max_altitude': 55,
    }

    return activity


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


@patch(TRACKS_SERVICE + '.get_files')
def test_save_data_no_sts_files(mck_files):
    mck_files.return_value = []

    actual = TracksService(trip=TripFactory.build()).save_data()

    assert actual == f'No sts files in {settings.MEDIA_ROOT}/tracks'


@patch(TRACKS_SERVICE + '.track_list_for_update')
@patch(TRACKS_SERVICE + '.get_files')
def test_save_data_everything_is_updated(mck_files, mck_tracks):
    mck_files.return_value = ['x']
    mck_tracks.return_value = None

    actual = TracksService(trip=TripFactory.build()).save_data()

    assert actual == 'All tracks are updated'


@patch(TRACKS_SERVICE + '.get_data_from_sts_file')
@patch(TRACKS_SERVICE + '.track_list_for_update')
@patch(TRACKS_SERVICE + '.get_files')
def test_save_data_save_track_data(mck_files, mck_tracks, mck_data, _activity):
    trip = TripFactory()
    mck_files.return_value = ['x']
    mck_tracks.return_value = ['y']
    mck_data.return_value = _activity

    TracksService(trip=trip).save_data()

    actual = Track.objects.last()

    assert actual.title == 'y'
    assert actual.date == datetime(2022, 1, 1, 3, 2, 1, tzinfo=timezone.utc)
    assert actual.activity_type == 'cycling'
    assert actual.trip.title == 'Trip'


@patch(TRACKS_SERVICE + '.get_data_from_sts_file')
@patch(TRACKS_SERVICE + '.track_list_for_update')
@patch(TRACKS_SERVICE + '.get_files')
def test_save_data_save_track_statistic_data(mck_files, mck_tracks, mck_data, _activity):
    trip = TripFactory()
    mck_files.return_value = ['x']
    mck_tracks.return_value = ['y']
    mck_data.return_value = _activity

    TracksService(trip=trip).save_data()

    actual = Statistic.objects.last()

    assert actual.total_km == 12.345
    assert actual.total_time_seconds == 1918.1
    assert round(actual.avg_speed, 2) == 23.40
    assert round(actual.max_speed, 2) == 47.52
    assert actual.calories == 33.0
    assert actual.avg_cadence == None
    assert actual.avg_heart == None
    assert actual.max_heart == None
    assert actual.avg_temperature == None
    assert actual.ascent == 111.0
    assert actual.descent == 222.0
    assert actual.min_altitude == 5
    assert actual.max_altitude == 55


@patch(TRACKS_SERVICE + '.get_data_from_sts_file')
@patch(TRACKS_SERVICE + '.track_list_for_update')
@patch(TRACKS_SERVICE + '.get_files')
def test_save_data_save_success(mck_files, mck_tracks, mck_data, _activity):
    trip = TripFactory()
    mck_files.return_value = ['x']
    mck_tracks.return_value = ['y']
    mck_data.return_value = _activity

    actual = TracksService(trip=trip).save_data()

    assert actual == 'Successfully synced data from sts files'


def test_sts_file_list(fs):
    directory = os.path.join(settings.MEDIA_ROOT, 'tracks')
    fs.create_file(os.path.join(directory, '1.sts'))
    fs.create_file(os.path.join(directory, '2.sts'))
    fs.create_file(os.path.join(directory, '3.xxx'))

    actual = TracksService(trip=TripFactory.build()).get_files()

    assert actual == ['1', '2']


def test_track_list_for_update():
    track = TrackFactory()

    files = ['999', '111']

    actual = TracksService(trip=track.trip).track_list_for_update(files)

    assert actual == ['111']


@patch('json.load')
def test_get_data_from_sts_file(mck, fs, _activity):
    fs.create_file(os.path.join(settings.MEDIA_ROOT, 'tracks', 'XXX.sts'))

    mck.return_value = _activity

    actual = TracksService().get_data_from_sts_file('XXX')

    assert actual == _activity


def test_get_data_from_sts_file_no_file(fs):
    actual = TracksService().get_data_from_sts_file('XXX')

    assert not actual
