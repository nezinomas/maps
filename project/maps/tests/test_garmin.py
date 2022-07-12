import os
from datetime import datetime, timezone

import pytest
from django.conf import settings
from mock import Mock, patch

from ..factories import TrackFactory, TripFactory
from ..models import Statistic, Track
from ..utils import garmin

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def _garmin_api(monkeypatch):
    mock_func = 'project.maps.utils.garmin.get_api'
    monkeypatch.setattr(mock_func, lambda: 'API')


@pytest.fixture
def _activity():
    return {
        'activityId': 999,
        'activityName': 'Vilnius Road Cycling',
        'startTimeLocal': '2022-01-01 05:02:11',
        'startTimeGMT': '2022-01-01 03:02:01',
        'activityType': {
            'typeId': 10,
            'typeKey': 'road_biking',
        },
        'distance': 12345.0,
        'movingDuration': 1918.1,
        'elevationGain': 111.0,
        'elevationLoss': 222.0,
        'averageSpeed': 6.5,
        'maxSpeed': 13.2,
        'startLatitude': 55.555,
        'startLongitude': 44.444,
        'calories': 33.0,
        'averageHR': None,
        'maxHR': None,
        'beginTimestamp': 1640998921000,  # 2022-1-1 3:2:1
        'minElevation': 5,
        'maxElevation': 55,
        'locationName': 'Vilnius',
        'lapCount': 3,
        'endLatitude': 66.666,
        'endLongitude': 77.777,
    }


@pytest.mark.freeze_time('2022-1-1')
@patch('project.maps.utils.garmin.get_api', return_value=None)
def test_get_data_failed_get_api(mck, fs):
    TripFactory()

    actual = garmin.get_data()

    assert actual == 'Error occurred during Garmin Connect communication'


@pytest.mark.freeze_time('2022-1-1')
@patch('project.maps.utils.garmin.Garmin.get_activities', side_effect=Exception('XXX'))
def test_get_data_failed_get_activities(mck, fs):
    TripFactory()

    actual = garmin.get_data()

    assert actual == 'Error occurred during getting garmin activities'


@pytest.mark.freeze_time('2022-1-1')
@patch('project.maps.utils.garmin.get_activities')
def test_get_data_no_cycling_activities(mck, fs):
    TripFactory()

    mck.return_value = [{'activityType': {'typeKey': 'XXX'}}]
    actual = garmin.get_data()

    assert actual == 'No cycling activities found'


@pytest.mark.freeze_time('1111-1-1')
def test_get_data_today_smaller_than_trip_start_date(_activity, fs):
    TripFactory()

    actual = garmin.get_data()
    assert actual == 'No trip found'


@pytest.mark.freeze_time('3333-1-1')
def test_get_data_today_greater_than_trip_end_date(_activity, fs):
    TripFactory()

    actual = garmin.get_data()
    assert actual == 'No trip found'


@pytest.mark.freeze_time('2022-1-1')
def test_get_data_no_trip(_activity):
    actual = garmin.get_data()
    assert actual == 'No trip found'


@pytest.mark.freeze_time('3333-1-1')
@patch('project.maps.utils.garmin.save_tcx_file')
@patch('project.maps.utils.garmin.get_activities')
def test_get_data_no_trip(mck_get, mck_write, _activity):
    mck_get.return_value = [_activity]

    actual = garmin.get_data()
    assert actual == 'No trip found'


@pytest.mark.freeze_time('2022-1-1')
@patch('project.maps.utils.garmin.save_tcx_file', return_value='XXX')
@patch('project.maps.utils.garmin.get_activities')
def test_get_data_faile_to_save_files(mck_get, mck_write, _activity, fs):
    TripFactory()

    mck_get.return_value = [_activity]

    actual = garmin.get_data()
    assert actual == 'Error occurred during saving tcx file: XXX'


@pytest.mark.freeze_time('2022-1-1')
@patch('project.maps.utils.garmin.save_tcx_file', return_value=None)
@patch('project.maps.utils.garmin.get_activities')
def test_get_data_success(mck_get, mck_write, _activity, fs):
    TripFactory()

    mck_get.return_value = [_activity]

    actual = garmin.get_data()
    assert actual == 'Successfully synced data from Garmin Connect'


def test_create_track_exists(_activity, fs):
    trip = TripFactory()
    track = TrackFactory()
    tracks = Track.objects.all().values_list('title', flat=True)

    actual = garmin.create_track(trip, _activity, tracks)

    assert not actual


def test_create_track_not_exists(_activity, fs):
    trip = TripFactory()
    tracks = Track.objects.all().values_list('title', flat=True)

    actual = garmin.create_track(trip, _activity, tracks)

    assert actual.title == '999'
    assert actual.date == datetime(2022, 1, 1, 3, 2, 1, tzinfo=timezone.utc)

    actual = Track.objects.all()
    assert actual.count() == 1


def test_filter_non_cycling_activities():
    activites = [
        {'activityType': { 'typeKey': 'xxx'}},
        {'activityType': { 'typeKey': 'biking'}},
        {'activityType': { 'typeKey': 'road_biking'}},
        {'activityType': { 'typeKey': 'cycling'}},
        {'activityType': { 'typeKey': 'road_cycling'}},
        {'activityType': { 'typeKey': 'running'}},
    ]

    actual = garmin.filter_non_cycling_activities(activites)

    assert len(actual) == 4

    for activity in actual:
        assert any(x in activity['activityType']['typeKey'] for x in ('biking', 'cycling'))


def test_tcx_file_not_exists(fs, _activity):
    folder = os.path.join(settings.MEDIA_ROOT, 'tracks')
    file = os.path.join(folder, '999.tcx')

    api = Mock()
    api.download_activity.return_value = b'tcx data'

    garmin.save_tcx_file(api, [_activity])

    with open(file, 'r') as f:
        assert f.read() == 'tcx data'


def test_tcx_file_exists(fs, _activity):
    file = os.path.join(settings.MEDIA_ROOT, 'tracks', '999.tcx')
    fs.create_file(file, contents='test')

    api = Mock()

    garmin.save_tcx_file(api, [_activity])

    assert  api.download_activity.call_count == 0

    with open(file, 'r') as f:
        assert f.read() == 'test'


def test_create_track_statistic(_activity):
    track = TrackFactory()

    garmin.create_track_statistic(_activity, track)

    actual = Statistic.objects.all()

    assert actual.count() == 1

    actual = actual[0]

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
    assert actual.track == track


def test_create_track_statistic_no_track(_activity):
    track = None

    garmin.create_track_statistic(_activity, track)

    actual = Statistic.objects.all()

    assert actual.count() == 0
