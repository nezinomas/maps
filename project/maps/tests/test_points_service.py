import os
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from django.conf import settings
from mock import patch

from ..factories import PointFactory, TrackFactory, TripFactory
from ..models import Point
from ..utils.points_service import PointsService

pytestmark = pytest.mark.django_db


@pytest.fixture
def _point():
    point = SimpleNamespace()

    point.TPX_speed = 5.0
    point.cadence = 80
    point.distance = 6.0
    point.elevation = 7.0
    point.hr_value = 111
    point.latitude = 44.44
    point.longitude = 55.55
    point.time = datetime(2022, 1, 1, 3, 2, 1)
    point.watts = 0.1

    return point


def test_update_points_no_trip():
    actual = PointsService().update_points()

    assert actual == 'No active trip'


def test_update_all_points_no_trip():
    actual = PointsService().update_all_points()

    assert actual == 'No active trip'


@pytest.mark.freeze_time('2022-1-1')
def test_get_tracks_with_no_points():
    PointFactory()
    track = TrackFactory(title='1')

    actual = PointsService().get_tracks_with_no_points()

    assert list(actual) == [track]


@pytest.mark.freeze_time('2022-1-1')
def test_get_tracks_with_no_points_ordering_by_date_desc():
    PointFactory()
    track1 = TrackFactory(title='2', date=datetime(2222, 1, 1))
    track2 = TrackFactory(title='1', date=datetime(1111, 1, 1))

    actual = PointsService().get_tracks_with_no_points()

    assert list(actual) == [track1, track2]


@pytest.mark.freeze_time('2022-1-1')
def test_get_tracks_with_no_points_all_good():
    PointFactory()

    actual = PointsService().get_tracks_with_no_points()

    assert not actual


@patch('project.maps.utils.points_service.TCXReader.read')
def test_get_data_from_tcx_file(mck, fs, project_fs, _point):
    trip = TripFactory()
    fs.create_file(os.path.join(settings.MEDIA_ROOT, 'tracks', str(trip.pk), '999.tcx'))

    data = SimpleNamespace(trackpoints=[_point])
    mck.return_value = data

    actual = PointsService(trip).get_data_from_tcx_file('999')

    assert actual == data


def test_get_data_from_tcx_file_no_file(fs, project_fs, _point):
    actual = PointsService(TripFactory()).get_data_from_tcx_file('999')

    assert not actual


@pytest.mark.freeze_time('2022-1-1')
@patch('project.maps.utils.points_service.PointsService.get_data_from_tcx_file')
def test_points_to_db_one(mck, _point):
    mck.return_value = SimpleNamespace(trackpoints=[_point])

    track = TrackFactory()

    PointsService().points_to_db([track])

    actual = Point.objects.last()

    assert actual.track == track

    assert actual.latitude == 44.44
    assert actual.longitude == 55.55
    assert actual.altitude == 7.0
    assert actual.distance_meters  == 6.0
    assert actual.cadence == 80
    assert actual.heart_rate == 111
    assert actual.datetime == datetime(2022, 1, 1, 1, 2, 1, tzinfo=timezone.utc)


@pytest.mark.freeze_time('2022-1-1')
@patch('project.maps.utils.points_service.PointsService.get_data_from_tcx_file')
def test_points_to_db_two_points(mck, _point):
    mck.return_value = SimpleNamespace(trackpoints=[_point, _point])

    track = TrackFactory()
    PointsService().points_to_db([track])

    actual = Point.objects.all()

    assert actual.count() == 2


@pytest.mark.freeze_time('2022-1-1')
def test_points_to_js(fs, project_fs):
    # create template in fake filesystem
    template = os.path.join(settings.SITE_ROOT, 'maps', 'templates', 'maps', 'points.html')
    fs.create_file(template)

    dir_ = os.path.join(settings.MEDIA_ROOT, 'points')

    track = TrackFactory()
    PointsService().points_to_js([track])

    assert os.path.exists(os.path.join(dir_, f'{track.trip.pk}-points.js'))
