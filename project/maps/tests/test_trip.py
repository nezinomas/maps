import pytest

from ..factories import TripFactory
from ..utils.common import get_trip

pytestmark = pytest.mark.django_db


@pytest.mark.freeze_time('1111-1-1')
def test_trip_not_started():
    TripFactory()

    actual = get_trip()

    assert not actual


@pytest.mark.freeze_time('3333-1-1')
def test_trip_ended(project_fs):
    TripFactory()

    actual = get_trip()

    assert not actual


@pytest.mark.freeze_time('2022-1-1')
def test_trip_exists(project_fs):
    _trip = TripFactory()

    actual = get_trip()

    assert actual == _trip


@pytest.mark.freeze_time('3333-1-1')
def test_trip_not_exists():
    actual = get_trip()

    assert not actual
