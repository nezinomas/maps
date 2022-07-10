from datetime import date, datetime, timezone

import pytest
from mock import patch

from ..factories import TrackFactory, TripFactory
from ..models import Track
from ..utils import garmin

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def _gamin_api(monkeypatch):
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
@patch('project.maps.utils.garmin.save_tcx_file')
@patch('project.maps.utils.garmin.get_activities')
def test_get_data(mck_get, mck_write, _activity):
    TripFactory()

    mck_get.return_value = [_activity]

    garmin.get_data()

    actual = Track.objects.all()

    assert actual.count() == 1
    assert actual[0].title == '999'
    assert actual[0].date == datetime(2022, 1, 1, 3, 2, 1, tzinfo=timezone.utc)

    assert mck_write.call_count == 1


@pytest.mark.freeze_time('2022-1-1')
@patch('project.maps.utils.garmin.save_tcx_file')
@patch('project.maps.utils.garmin.get_activities')
def test_get_data_track_exists(mck_get, mck_write, _activity):
    TrackFactory()

    mck_get.return_value = [_activity]

    garmin.get_data()

    actual = Track.objects.all()

    assert actual.count() == 1
    assert mck_write.call_count == 0


@pytest.mark.freeze_time('3333-1-1')
@patch('project.maps.utils.garmin.save_tcx_file')
@patch('project.maps.utils.garmin.get_activities')
def test_get_data_today_greater_than_trip_end_date(mck_get, mck_write, _activity):
    TripFactory()

    mck_get.return_value = [_activity]

    garmin.get_data()

    actual = Track.objects.all()

    assert actual.count() == 0
    assert mck_write.call_count == 0


@pytest.mark.freeze_time('2022-1-1')
@patch('project.maps.utils.garmin.save_tcx_file')
@patch('project.maps.utils.garmin.get_activities')
def test_get_data_activity_not_cycling(mck_get, mck_write, _activity):
    TripFactory()

    _activity['activityType']['typeKey'] = 'running'
    mck_get.return_value = [_activity]

    garmin.get_data()

    actual = Track.objects.all()

    assert actual.count() == 0
    assert mck_write.call_count == 0
