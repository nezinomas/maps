import os
from pathlib import Path

import pytest
from django.conf import settings
from django.test import override_settings
from mock import Mock, patch

from ..factories import TripFactory
from ..utils.garmin_service import GarminApi, GarminService, GarminServiceError

GARMIN_API = "project.maps.utils.garmin_service.GarminApi"
GARMIN_SERVICE = "project.maps.utils.garmin_service.GarminService"
GET_TRIP = "project.maps.utils.garmin_service.get_trip"

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def mck_download_tcx(monkeypatch):
    monkeypatch.setattr(f"{GARMIN_API}._create_api", Mock())


def test_garmin_service_init_with_trip():
    actual = GarminService(trip=TripFactory.build())

    assert actual.trip.title == "Trip"


@patch(GET_TRIP)
def test_garmin_service_init_without_trip(mck_download_tcx):
    mck_download_tcx.return_value = TripFactory.build()
    actual = GarminService()

    assert actual.trip.title == "Trip"


@patch(GET_TRIP)
def test_get_data_no_trip(mck_download_tcx):
    mck_download_tcx.return_value = None
    actual = GarminService().get_data()

    assert actual == "No trip found"


def test_get_data_failed_get_api(monkeypatch):
    monkeypatch.setattr(GARMIN_API, lambda: None)

    actual = GarminService(trip=TripFactory.build()).get_data()

    assert actual == "Error occurred during Garmin Connect communication"


@patch(
    f"{GARMIN_SERVICE}._fetch_activities",
    side_effect=GarminServiceError("X"),
)
def test_get_data_failed_get_activities(mck_download_tcx):
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


@patch(f"{GARMIN_API}.download_tcx", return_value=b"tcx data")
def test_tcx_new_file(mck_download_tcx, tmp_path):
    trip = TripFactory()

    _activities = [
        {
            "activityId": 999,
        }
    ]

    tmp_path.mkdir(parents=True, exist_ok=True)
    with override_settings(MEDIA_ROOT=tmp_path):
        GarminService(trip=trip)._save_activities(_activities)

        assert mck_download_tcx.call_count == 1

        file = Path(settings.MEDIA_ROOT, "tracks", str(trip.pk), "999.tcx")
        with open(file, "r") as f:
            assert f.read() == "tcx data"


@patch(f"{GARMIN_API}.download_tcx", return_value=b"tcx data")
def test_tcx_file_exist(mck_download_tcx, fs):
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

    obj = GarminService(trip=trip)._save_activities(_activities)

    assert mck_download_tcx.call_count == 0

    with open(file_tcx, "r") as f:
        assert f.read() == "test"

    with open(activity_file, "r") as f:
        assert f.read() == "test"
