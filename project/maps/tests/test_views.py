from django.contrib.auth.models import User
import pytest
from django.urls import resolve, reverse

from .. import views
from ..factories import TripFactory

pytestmark = pytest.mark.django_db


# ---------------------------------------------------------------------------------------
#                                                                          Trip List View
# ---------------------------------------------------------------------------------------
def test_trips_func():
    view = resolve('/')

    assert views.Trips == view.func.view_class


def test_trips_200(client):
    url = reverse('maps:trips')
    response = client.get(url, follow=True)

    assert response.status_code == 200


def test_trips_list(client, project_fs):
    TripFactory(title='Trip 1')
    TripFactory(title='Trip 2')

    url = reverse('maps:trips')
    response = client.get(url)

    content = response.content.decode('utf8')

    assert 'Trip 1' in content
    assert 'Trip 2' in content


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
#                                                                    Donwload Garmin Data
# ---------------------------------------------------------------------------------------
def test_download_tcx_func():
    view = resolve('/trip-title/download_tcx/')

    assert views.DownloadTcx == view.func.view_class


def test_download_tcx_index_200(client_logged):
    trip = TripFactory()

    url = reverse('maps:download_tcx', kwargs={'trip': trip.slug})
    response = client_logged.get(url, follow=True)

    assert response.status_code == 200


def test_download_tcx_not_logged(client):
    trip = TripFactory()

    url = reverse('maps:download_tcx', kwargs={'trip': trip.slug})
    response = client.get(url)

    assert response.status_code == 302


# ---------------------------------------------------------------------------------------
#                                                                         New Points View
# ---------------------------------------------------------------------------------------
def test_update_points_func():
    view = resolve('/trip-title/update_points/')

    assert views.SaveNewPoints == view.func.view_class


def test_update_points_index_200(client_logged):
    trip = TripFactory()

    url = reverse('maps:update_points', kwargs={'trip': trip.slug})
    response = client_logged.get(url, follow=True)

    assert response.status_code == 200


def test_update_points_not_logged(client):
    trip = TripFactory()

    url = reverse('maps:update_points', kwargs={'trip': trip.slug})
    response = client.get(url)

    assert response.status_code == 302


# ---------------------------------------------------------------------------------------
#                                                                     Rewrite Points View
# ---------------------------------------------------------------------------------------
def test_update_all_points_func():
    view = resolve('/trip-title/update_all_points/')

    assert views.RewriteAllPoints == view.func.view_class


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


# ---------------------------------------------------------------------------------------
#                                                               Regenerate Points JS File
# ---------------------------------------------------------------------------------------
def test_regenerate_points_file_func():
    view = resolve('/trip-title/regenerate_points_file/')

    assert views.RegeneratePointsFile == view.func.view_class


def test_regenerate_points_file_index_200(client_logged):
    trip = TripFactory()

    url = reverse('maps:regenerate_points_file', kwargs={'trip': trip.slug})
    response = client_logged.get(url, follow=True)

    assert response.status_code == 200


def test_regenerate_points_file_not_logged(client):
    trip = TripFactory()

    url = reverse('maps:regenerate_points_file', kwargs={'trip': trip.slug})
    response = client.get(url)

    assert response.status_code == 302


# ---------------------------------------------------------------------------------------
#                                                                          New Tracks View
# ---------------------------------------------------------------------------------------
def test_update_tracks_func():
    view = resolve('/trip-title/update_tracks/')

    assert views.SaveNewTracks == view.func.view_class


def test_update_tracks_index_200(client_logged):
    trip = TripFactory()

    url = reverse('maps:update_tracks', kwargs={'trip': trip.slug})
    response = client_logged.get(url, follow=True)

    assert response.status_code == 200


def test_update_tracks_not_logged(client):
    trip = TripFactory()

    url = reverse('maps:update_tracks', kwargs={'trip': trip.slug})
    response = client.get(url)

    assert response.status_code == 302


# ---------------------------------------------------------------------------------------
#                                                                  Rewrite All Tracks View
# ---------------------------------------------------------------------------------------
def test_update_all_tracks_func():
    view = resolve('/trip-title/update_all_tracks/')

    assert views.RewriteAllTracks == view.func.view_class


def test_update_all_tracks_index_200(client_logged):
    trip = TripFactory()

    url = reverse('maps:update_all_tracks', kwargs={'trip': trip.slug})
    response = client_logged.get(url, follow=True)

    assert response.status_code == 200


def test_update_all_tracks_not_logged(client):
    trip = TripFactory()

    url = reverse('maps:update_all_tracks', kwargs={'trip': trip.slug})
    response = client.get(url)

    assert response.status_code == 302

