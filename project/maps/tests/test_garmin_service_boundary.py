from datetime import date

import pytest
from mock import patch

from project.maps.factories import TripFactory
from project.maps.utils.garmin_service import GarminService


@patch("project.maps.utils.garmin_service.GarminService._save_activities")
@patch("project.maps.utils.garmin_service.GarminService._fetch_activities")
def test_get_data_filter_midnight_utc_is_included(mck_activities, mck_save):
    trip = TripFactory.build(start_date=date(2022, 1, 1), end_date=date(2022, 1, 10))
    mck_activities.return_value = [
        {
            "activityType": {"typeKey": "cycling"},
            "startTimeGMT": "2022-01-01 00:00:00",
        }
    ]

    actual = GarminService(trip=trip).get_data()

    # If it's correctly parsed as UTC, 2022-01-01 00:00:00 is >= 2022-01-01 00:00:00 UTC
    assert actual == "Successfully synced data from Garmin Connect"
