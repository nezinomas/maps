import os
from pathlib import Path

import pytest
from django.conf import settings
from django.test import override_settings
from mock import Mock, patch

from ..factories import TripFactory
from ..utils.garmin_service import GarminService, GarminServiceError

GARMIN_SERVICE = "project.maps.utils.garmin_service.GarminService"
GET_TRIP = "project.maps.utils.garmin_service.get_trip"

pytestmark = pytest.mark.django_db


@pytest.fixture(name="garmin_api", autouse=True)
def fixture_garmin_api(monkeypatch):
    mock_func = "project.maps.utils.garmin_service.create_api"

    mck = Mock()
    mck.download_activity.return_value = b"tcx data"

    return monkeypatch.setattr(mock_func, lambda: mck)


def test_garmin_service_init_with_trip():
    actual = GarminService(trip=TripFactory.build())

    assert actual.trip.title == "Trip"


@patch(GET_TRIP)
def test_garmin_service_init_without_trip(mck):
    mck.return_value = TripFactory.build()
    actual = GarminService()

    assert actual.trip.title == "Trip"


@patch(GET_TRIP)
def test_get_data_no_trip(mck):
    mck.return_value = None
    actual = GarminService().get_data()

    assert actual == "No trip found"


@patch("project.maps.utils.garmin_service.create_api")
def test_get_data_failed_get_api(garmin_api):
    garmin_api.return_value = None

    actual = GarminService(trip=TripFactory.build()).get_data()

    assert actual == "Error occurred during Garmin Connect communication"


@patch(
    f"{GARMIN_SERVICE}._fetch_activities",
    side_effect=GarminServiceError("X"),
)
def test_get_data_failed_get_activities(mck):
    actual = GarminService(trip=TripFactory.build()).get_data()

    assert actual == "Error: X"


@patch(f"{GARMIN_SERVICE}._fetch_activities")
def test_get_data_filter_non_cyclig_activities(mck_activities):
    mck_activities.return_value = [
        {"activityType": {"typeKey": "XXX"}},
    ]

    actual = GarminService(trip=TripFactory.build()).get_data()

    assert actual == "Nothing to sync"


@patch(f"{GARMIN_SERVICE}._fetch_activities")
def test_get_data_filter_past_activities(mck_activities):
    mck_activities.return_value = [
        {
            "activityType": {"typeKey": "cycling"},
            "startTimeGMT": "1974-01-01 03:02:01",
        }
    ]

    actual = GarminService(trip=TripFactory.build()).get_data()

    assert actual == "Nothing to sync"


@patch(f"{GARMIN_SERVICE}._fetch_activities")
def test_get_data_filter_future_activities(mck_activities):
    mck_activities.return_value = [
        {
            "activityType": {"typeKey": "cycling"},
            "startTimeGMT": "2222-01-01 03:02:01",
        }
    ]

    actual = GarminService(trip=TripFactory.build()).get_data()

    assert actual == "Nothing to sync"


@patch(f"{GARMIN_SERVICE}._save_activities", side_effect=GarminServiceError("X"))
@patch(f"{GARMIN_SERVICE}._fetch_activities")
def test_get_data_save_file_failed(mck_activities, mck_save):
    mck_activities.return_value = [
        {
            "activityType": {"typeKey": "cycling"},
            "startTimeGMT": "2022-01-01 03:02:01",
        }
    ]

    actual = GarminService(trip=TripFactory.build()).get_data()

    assert actual == "Error: X"


@patch(f"{GARMIN_SERVICE}._save_activities")
@patch(f"{GARMIN_SERVICE}._fetch_activities")
def test_get_data_success(mck_activities, mck_save):
    mck_activities.return_value = [
        {
            "activityType": {"typeKey": "cycling"},
            "startTimeGMT": "2022-01-01 03:02:01",
        }
    ]

    actual = GarminService(trip=TripFactory.build()).get_data()

    assert actual == "Successfully synced data from Garmin Connect"


def test_tcx_new_file(garmin_api, tmp_path):
    trip = TripFactory()

    _activities = [
        {
            "activityId": 999,
        }
    ]

    tmp_path.mkdir(parents=True, exist_ok=True)
    with override_settings(MEDIA_ROOT=tmp_path):
        obj = GarminService(trip=trip, api=garmin_api)

        obj._save_activities(_activities)

        assert obj.api.download_activity.call_count == 1

        file = Path(settings.MEDIA_ROOT, "tracks", str(trip.pk), "999.tcx")
        with open(file, "r") as f:
            assert f.read() == "tcx data"


def test_tcx_file_exist(garmin_api, fs):
    trip = TripFactory()
    _activities = [
        {
            "activityId": 999,
        }
    ]

    file_tcx = os.path.join(settings.MEDIA_ROOT, "tracks", str(trip.pk), "999.tcx")
    fs.create_file(file_tcx, contents="test")

    activity_file = os.path.join(settings.MEDIA_ROOT, "tracks", str(trip.pk), "999")
    fs.create_file(activity_file, contents="test")

    obj = GarminService(trip=trip, api=garmin_api)

    # save activities
    obj._save_activities(_activities)

    assert obj.api.download_activity.call_count == 0

    with open(file_tcx, "r") as f:
        assert f.read() == "test"

    with open(activity_file, "r") as f:
        assert f.read() == "test"
