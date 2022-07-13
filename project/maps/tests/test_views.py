from django.contrib.auth.models import User
import pytest
from django.urls import resolve, reverse

from .. import views
from ..factories import TripFactory

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------------------
#                                                                          Utilities View
# ---------------------------------------------------------------------------------------
def test_utils_func():
    view = resolve('/trip-title/utils/')

    assert views.Utils == view.func.view_class


def test_utils_index_200(client_logged):
    trip = TripFactory()

    url = reverse('maps:utils', kwargs={'trip': trip.slug})
    response = client_logged.get(url, follow=True)

    assert response.status_code == 200


def test_utils_not_logged(client):
    trip = TripFactory()

    url = reverse('maps:utils', kwargs={'trip': trip.slug})
    response = client.get(url)

    assert response.status_code == 302


# ---------------------------------------------------------------------------------------
#                                                                  Update All Points View
# ---------------------------------------------------------------------------------------
def test_update_all_points_func():
    view = resolve('/trip-title/update_all_points/')

    assert views.UpdateAllPoints == view.func.view_class


def test_update_all_points_index_200(client_logged):
    trip = TripFactory()

    url = reverse('maps:update_all_points', kwargs={'trip': trip.slug})
    response = client_logged.get(url, follow=True)

    assert response.status_code == 200


def test_update_all_points_not_logged(client):
    trip = TripFactory()

    url = reverse('maps:update_all_points', kwargs={'trip': trip.slug})
    response = client.get(url)

    assert response.status_code == 302
