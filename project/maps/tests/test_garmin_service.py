import json
import os
from pathlib import Path

import pytest
from django.conf import settings
from django.test import override_settings
from mock import Mock, patch

from ..factories import TripFactory
from ..utils.garmin_service import GarminService

GARMIN_SERVICE = "project.maps.utils.garmin_service.GarminService"
GET_TRIP = "project.maps.utils.garmin_service.get_trip"

pytestmark = pytest.mark.django_db


@pytest.fixture(name="garmin_api", autouse=True)
def fixture_garmin_api(monkeypatch):
    mock_func = f"{GARMIN_SERVICE}.get_api"
    monkeypatch.setattr(mock_func, lambda x: "API")


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

    assert actual == ["No trip found"]


@patch(f"{GARMIN_SERVICE}.get_api")
def test_get_data_failed_get_api(mck_api):
    mck_api.return_value = None

    actual = GarminService(trip=TripFactory.build()).get_data()

    assert actual == ["Error occurred during Garmin Connect communication"]


@patch("project.maps.utils.garmin_service.Garmin.get_activities")
def test_get_data_failed_get_activities(mck_activities):
    mck_activities.side_effect = Exception("XXX")

    actual = GarminService(trip=TripFactory.build()).get_data()

    assert actual == ["Error occurred during getting garmin activities"]


@patch(f"{GARMIN_SERVICE}.get_activities")
def test_get_data_filter_non_cyclig_activities(mck_activities):
    mck_activities.return_value = [
        {"activityType": {"typeKey": "XXX"}},
    ]

    actual = GarminService(trip=TripFactory.build()).get_data()

    assert actual == ["Nothing to sync"]


@patch(f"{GARMIN_SERVICE}.get_activities")
def test_get_data_filter_past_activities(mck_activities):
    mck_activities.return_value = [
        {
            "activityType": {"typeKey": "cycling"},
            "startTimeGMT": "1974-01-01 03:02:01",
        }
    ]

    actual = GarminService(trip=TripFactory.build()).get_data()

    assert actual == ["Nothing to sync"]


@patch(f"{GARMIN_SERVICE}.get_activities")
def test_get_data_filter_future_activities(mck_activities):
    mck_activities.return_value = [
        {
            "activityType": {"typeKey": "cycling"},
            "startTimeGMT": "2222-01-01 03:02:01",
        }
    ]

    actual = GarminService(trip=TripFactory.build()).get_data()

    assert actual == ["Nothing to sync"]


@patch(f"{GARMIN_SERVICE}.save_files")
@patch(f"{GARMIN_SERVICE}.get_activities")
def test_get_data_save_file_failed(mck_activities, mck_save):
    mck_activities.return_value = [
        {
            "activityType": {"typeKey": "cycling"},
            "startTimeGMT": "2022-01-01 03:02:01",
        }
    ]
    mck_save.return_value = "XXX"

    actual = GarminService(trip=TripFactory.build()).get_data()

    assert actual == ["Error occurred during saving tcx file: XXX"]


@patch(f"{GARMIN_SERVICE}.save_files")
@patch(f"{GARMIN_SERVICE}.get_activities")
def test_get_data_success(mck_activities, mck_save):
    mck_activities.return_value = [
        {
            "activityType": {"typeKey": "cycling"},
            "startTimeGMT": "2022-01-01 03:02:01",
        }
    ]
    mck_save.return_value = None

    actual = GarminService(trip=TripFactory.build()).get_data()

    assert actual == ["Successfully synced data from Garmin Connect"]


def test_tcx_new_file(tmp_path):
    trip = TripFactory()

    _activities = [
        {
            "activityId": 999,
        }
    ]

    api = Mock()
    api.download_activity.return_value = b"tcx data"

    tmp_path.mkdir(parents=True, exist_ok=True)
    with override_settings(MEDIA_ROOT=tmp_path):
        GarminService(trip=trip).save_files(api, _activities)

        file = Path(settings.MEDIA_ROOT, "tracks", str(trip.pk), "999.tcx")
        with open(file, "r") as f:
            assert f.read() == "tcx data"


def test_tcx_and_sts_files_exists(fs):
    _activities = [
        {
            "activityId": 999,
        }
    ]

    file_tcx = os.path.join(settings.MEDIA_ROOT, "tracks", "999.tcx")
    fs.create_file(file_tcx, contents="test")

    activity_file = os.path.join(settings.MEDIA_ROOT, "tracks", "999")
    fs.create_file(activity_file, contents="test")

    api = Mock()
    api.download_activity.return_value = b"tcx data"

    GarminService(trip="xxx").save_files(api, _activities)

    assert api.download_activity.call_count == 0

    with open(file_tcx, "r") as f:
        assert f.read() == "test"

    with open(activity_file, "r") as f:
        assert f.read() == "test"
