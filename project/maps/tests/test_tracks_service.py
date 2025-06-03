from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from django.contrib.gis.geos import LineString
from mock import patch

from ..factories import StatisticFactory, TrackFactory, TripFactory
from ..models import Statistic, Track
from ..utils.tracks_service import TracksService

pytestmark = pytest.mark.django_db


def test_init_trip():
    data = SimpleNamespace(
        trip=SimpleNamespace(title="T"), tracks_db=set(), tracks_disk=set()
    )
    actual = TracksService(data)

    assert actual.trip.title == "T"


def test_track_list():
    tracks = [
        {"title": "Track 001", "pk": 1},
        {"title": "Track 002", "pk": 2},
        {"title": "Track 003", "pk": 3},
    ]

    data = SimpleNamespace(trip="T", tracks_db=tracks, tracks_disk=set())

    actual = TracksService(data).tracks_db

    assert actual == {"Track 001", "Track 002", "Track 003"}


def test_track_title_pk_map():
    tracks = [
        {"title": "Track 001", "pk": 1},
        {"title": "Track 002", "pk": 2},
        {"title": "Track 003", "pk": 3},
    ]

    data = SimpleNamespace(trip="T", tracks_db=tracks, tracks_disk=set())

    actual = TracksService(data).tracks_title_pk_map

    assert actual == {"Track 001": 1, "Track 002": 2, "Track 003": 3}


def test_activity_files():
    activity_files = {"file1", "file2", "file3"}
    data = SimpleNamespace(trip="T", tracks_db=set(), tracks_disk=activity_files)

    actual = TracksService(data).tracks_disk

    assert actual == {"file1", "file2", "file3"}


def test_no_activity_files():
    data = SimpleNamespace(trip="T", tracks_db=set(), tracks_disk=set())

    actual = TracksService(data).tracks_disk

    assert actual == set()


def test_new_tracks():
    data = SimpleNamespace(
        trip=SimpleNamespace(title="T"),
        tracks_db=[{"title": "1", "pk": 1}],
        tracks_disk={"1", "2"},
    )
    actual = TracksService(data).new_tracks()
    assert actual == {"2"}


def test_no_new_tracks():
    data = SimpleNamespace(
        trip=SimpleNamespace(title="T"),
        tracks_db=[{"title": "1", "pk": 1}],
        tracks_disk={"1"},
    )
    actual = TracksService(data).new_tracks()

    assert actual == set()


@patch("project.maps.utils.parse_activity_file.get_statistic", return_value={})
@patch("project.maps.utils.parse_tcx_file.get_track_path")
@patch("project.maps.utils.parse_tcx_file.get_track_date")
def test_create_new_tracks(date_mock, path_mock, stats_mock):
    path_mock.return_value = LineString((5, 6), (7, 8))
    date_mock.return_value = datetime(2022, 3, 4, 5, 6, 7, tzinfo=timezone.utc)

    trip = TripFactory()
    data = SimpleNamespace(trip=trip, tracks_db=set(), tracks_disk={"1"})

    obj = TracksService(data)
    obj.create()

    assert Track.objects.count() == 1

    actual = Track.objects.get(title="1")
    assert actual.date == datetime(2022, 3, 4, 5, 6, 7, tzinfo=timezone.utc)
    assert actual.path.coords == ((5, 6), (7, 8))


@patch("project.maps.utils.parse_activity_file.get_statistic", return_value={})
@patch("project.maps.utils.parse_tcx_file.get_track_path")
@patch("project.maps.utils.parse_tcx_file.get_track_date")
def test_create_new_tracks_one_exists(date_mock, path_mock, stats_mock):
    path_mock.return_value = LineString((5, 6), (7, 8))
    date_mock.return_value = datetime(2022, 3, 4, 5, 6, 7, tzinfo=timezone.utc)

    trip = TripFactory()
    data = SimpleNamespace(
        trip=trip, tracks_db=[{"title": "1", "pk": 1}], tracks_disk={"1", "2"}
    )

    obj = TracksService(data)
    obj.create()

    assert Track.objects.count() == 1

    actual = Track.objects.get(title="2")
    assert actual.date == datetime(2022, 3, 4, 5, 6, 7, tzinfo=timezone.utc)
    assert actual.path.coords == ((5, 6), (7, 8))


@patch("project.maps.utils.parse_activity_file.get_statistic", return_value={})
@patch("project.maps.utils.parse_tcx_file.get_track_path")
@patch("project.maps.utils.parse_tcx_file.get_track_date")
def test_not_create_new_tracks(date_mock, path_mock, stats_mock):
    path_mock.return_value = LineString((5, 6), (7, 8))
    date_mock.return_value = datetime(2022, 3, 4, 5, 6, 7, tzinfo=timezone.utc)

    trip = TripFactory()
    data = SimpleNamespace(
        trip=trip, tracks_db=[{"title": "1", "pk": 1}], tracks_disk={"1"}
    )

    obj = TracksService(data)
    obj.create()

    assert Track.objects.count() == 0


@patch("project.maps.utils.parse_activity_file.get_statistic", return_value={})
@patch("project.maps.utils.parse_tcx_file.get_track_path")
@patch("project.maps.utils.parse_tcx_file.get_track_date")
def test_update_track(date_mock, path_mock, stats_mock):
    track = TrackFactory(title="1")

    path_mock.return_value = LineString((5, 6), (7, 8))
    date_mock.return_value = datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc)

    trip = TripFactory()
    data = SimpleNamespace(
        trip=trip, tracks_db=[{"title": track.title, "pk": track.pk}], tracks_disk={"1"}
    )

    obj = TracksService(data)
    obj.create_or_update()

    assert Track.objects.count() == 1

    actual = Track.objects.get(title="1")
    assert actual.date == datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
    assert actual.path.coords == ((5, 6), (7, 8))


@patch("project.maps.utils.parse_activity_file.get_statistic")
@patch("project.maps.utils.parse_tcx_file.get_track_path")
@patch("project.maps.utils.parse_tcx_file.get_track_date")
def test_create_new_statistic(date_mock, path_mock, stats_mock):
    path_mock.return_value = LineString((5, 6), (7, 8))
    date_mock.return_value = datetime(2022, 3, 4, 5, 6, 7, tzinfo=timezone.utc)
    stats_mock.return_value = {
        "total_km": 10.0,
        "total_time_seconds": 3600,
        "avg_speed": 2.5,
        "ascent": 100,
        "descent": 50,
        "min_altitude": 200,
        "max_altitude": 300,
    }

    data = SimpleNamespace(trip=TripFactory(), tracks_db=[], tracks_disk={"2"})

    obj = TracksService(data)
    obj.create()

    assert Statistic.objects.count() == 1

    actual = Statistic.objects.get(track__title="2")

    assert actual.total_km == 10.0
    assert actual.total_time_seconds == 3600
    assert actual.avg_speed == 2.5
    assert actual.ascent == 100
    assert actual.descent == 50
    assert actual.min_altitude == 200
    assert actual.max_altitude == 300


@patch("project.maps.utils.parse_activity_file.get_statistic")
@patch("project.maps.utils.parse_tcx_file.get_track_path")
@patch("project.maps.utils.parse_tcx_file.get_track_date")
def test_update_statistic(date_mock, path_mock, stats_mock):
    # mock return values
    date_mock.return_value = datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
    path_mock.return_value = LineString((5, 6), (7, 8))
    stats_mock.return_value = {
        "total_km": 20.0,
        "total_time_seconds": 7200,
        "avg_speed": 5.0,
        "ascent": 200,
        "descent": 100,
        "min_altitude": 300,
        "max_altitude": 400,
    }

    stats = StatisticFactory()

    trip = TripFactory()
    data = SimpleNamespace(
        trip=trip,
        tracks_db=[{"title": stats.track.title, "pk": stats.track.pk}],
        tracks_disk={stats.track.title},
    )

    obj = TracksService(data)
    obj.create_or_update()

    assert Track.objects.count() == 1
    assert Statistic.objects.count() == 1

    actual = Statistic.objects.last()
    assert actual.track == stats.track
    assert actual.total_km == 20.0
    assert actual.total_time_seconds == 7200
    assert actual.avg_speed == 5.0
    assert actual.ascent == 200
    assert actual.descent == 100
    assert actual.min_altitude == 300
    assert actual.max_altitude == 400
