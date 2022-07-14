import os
from datetime import datetime, timezone
from types import SimpleNamespace

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
    activity = SimpleNamespace()

    activity.activity_type = 'Biking'
    activity.distance = 12345.6
    activity.duration = 1918.1
    activity.avg_speed = 23.40
    activity.max_speed = 47.52
    activity.calories = 33
    activity.cadence_avg = 44.4
    activity.hr_avg = 55.5
    activity.hr_max = 200
    activity.ascent = 111.0
    activity.descent = 222.0
    activity.altitude_min = 6.0
    activity.altitude_max = 7.0
    activity.start_time = datetime(2022, 1, 1, 3, 2, 1, tzinfo=timezone.utc)

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
def test_save_data_no_tcx_files(mck_files):
    mck_files.return_value = []

    actual = TracksService(trip=TripFactory.build()).save_data()

    assert actual == f'No tcx files in {settings.MEDIA_ROOT}/tracks'


@patch(TRACKS_SERVICE + '.track_list_for_update')
@patch(TRACKS_SERVICE + '.get_files')
def test_save_data_no_tcx_files(mck_files, mck_tracks):
    mck_files.return_value = ['x']
    mck_tracks.return_value = None

    actual = TracksService(trip=TripFactory.build()).save_data()

    assert actual == 'All tracks are updated'


@patch(TRACKS_SERVICE + '.get_data_from_tcx_file')
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
    assert actual.activity_type == 'Biking'
    assert actual.trip.title == 'Trip'


@patch(TRACKS_SERVICE + '.get_data_from_tcx_file')
@patch(TRACKS_SERVICE + '.track_list_for_update')
@patch(TRACKS_SERVICE + '.get_files')
def test_save_data_save_track_statistic_data(mck_files, mck_tracks, mck_data, _activity):
    trip = TripFactory()
    mck_files.return_value = ['x']
    mck_tracks.return_value = ['y']
    mck_data.return_value = _activity

    TracksService(trip=trip).save_data()

    actual = Statistic.objects.last()

    assert round(actual.total_km, 2) == 12.35
    assert actual.total_time_seconds == 1918.1
    assert round(actual.avg_speed, 2) == 23.40
    assert round(actual.max_speed, 2) == 47.52
    assert actual.calories == 33.0
    assert actual.avg_cadence == 44.4
    assert actual.avg_heart == 55.5
    assert actual.max_heart == 200
    assert actual.avg_temperature == None
    assert actual.ascent == 111.0
    assert actual.descent == 222.0
    assert actual.min_altitude == 6.0
    assert actual.max_altitude == 7.0


@patch(TRACKS_SERVICE + '.get_data_from_tcx_file')
@patch(TRACKS_SERVICE + '.track_list_for_update')
@patch(TRACKS_SERVICE + '.get_files')
def test_save_data_save_success(mck_files, mck_tracks, mck_data, _activity):
    trip = TripFactory()
    mck_files.return_value = ['x']
    mck_tracks.return_value = ['y']
    mck_data.return_value = _activity

    actual = TracksService(trip=trip).save_data()

    assert actual == 'Successfully synced data from tcx files'


def test_tcx_file_list(fs):
    directory = os.path.join(settings.MEDIA_ROOT, 'tracks')
    fs.create_file(os.path.join(directory, '1.tcx'))
    fs.create_file(os.path.join(directory, '2.tcx'))
    fs.create_file(os.path.join(directory, '3.xxx'))


    actual = TracksService(trip=TripFactory.build()).get_files()

    assert actual == ['1', '2']


def test_track_list_for_update():
    track = TrackFactory()

    files = ['999', '111']

    actual = TracksService(trip=track.trip).track_list_for_update(files)

    assert actual == ['111']


@patch('project.maps.utils.tracks_service.TCXReader.read')
def test_get_data_from_tcx_file(mck, fs, _activity):
    fs.create_file(os.path.join(settings.MEDIA_ROOT, 'tracks', 'XXX.tcx'))

    mck.return_value = _activity

    actual = TracksService().get_data_from_tcx_file('XXX')

    assert actual == _activity


def test_get_data_from_tcx_file_no_file(fs):
    actual = TracksService().get_data_from_tcx_file('XXX')

    assert not actual
