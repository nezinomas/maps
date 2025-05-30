import pytest

from ..utils.parse_activity_file import get_statistic
from mock import patch

@pytest.fixture(name="garmin_activity")
def fixture_activity():
    return {
        "activityId": 999,
        "activityName": "Vilnius Road Cycling",
        "startTimeLocal": "2022-01-01 05:02:11",
        "startTimeGMT": "2022-01-01 03:02:01",
        "activityType": {
            "typeId": 10,
            "typeKey": "road_biking",
        },
        "distance": 12345.0,
        "movingDuration": 1918.1,
        "elevationGain": 111.0,
        "elevationLoss": 222.0,
        "averageSpeed": 6.5,
        "maxSpeed": 13.2,
        "startLatitude": 55.555,
        "startLongitude": 44.444,
        "calories": 33.0,
        "averageHR": None,
        "maxHR": None,
        "beginTimestamp": 1640998921000,  # 2022-1-1 3:2:1
        "minElevation": 5,
        "maxElevation": 55,
        "locationName": "Vilnius",
        "lapCount": 3,
        "endLatitude": 66.666,
        "endLongitude": 77.777,
    }


@patch("project.maps.utils.parse_activity_file.get_activity_content")
def test_activity_statistic(content_mck, garmin_activity):
    content_mck.return_value = garmin_activity

    actual = get_statistic("/path/to/activity/file")

    assert actual["start_time"] == "2022-01-01 03:02:01 +0000"
    assert actual["total_km"] == 12.345
    assert actual["total_time_seconds"] == 1918.1
    assert round(actual["avg_speed"], 2) == 23.40
    assert round(actual["max_speed"], 2) == 47.52
    assert actual["calories"] == 33.0
    assert actual["avg_cadence"] is None
    assert actual["avg_heart"] is None
    assert actual["max_heart"] is None
    assert actual["avg_temperature"] is None
    assert actual["ascent"] == 111.0
    assert actual["descent"] == 222.0
    assert actual["min_altitude"] == 5
    assert actual["max_altitude"] == 55
