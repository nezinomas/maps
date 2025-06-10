import pytest
from django.urls import resolve, reverse

from .. import views
from ..factories import TripFactory

pytestmark = pytest.mark.django_db


# -------------------------------------------------------------------------------------
#                                                                        Trip List View
# -------------------------------------------------------------------------------------
def test_trips_func():
    view = resolve("/")

    assert views.Trips == view.func.view_class


def test_trips_200(client):
    url = reverse("maps:trips")
    response = client.get(url, follow=True)

    assert response.status_code == 200


def test_trips_list(client):
    TripFactory(title="Trip 1")
    TripFactory(title="Trip 2")

    url = reverse("maps:trips")
    response = client.get(url)

    content = response.content.decode("utf8")

    assert "Trip 1" in content
    assert "Trip 2" in content


# -------------------------------------------------------------------------------------
#                                                                        Utilities View
# -------------------------------------------------------------------------------------
def test_utils_func():
    view = resolve("/utils/")

    assert views.Utils == view.func.view_class


def test_utils_index_not_logged(client):
    url = reverse("maps:utils_index")
    response = client.get(url, follow=True)

    assert response.resolver_match.view_name == "maps:login"


def test_utils_index_200(admin_client):
    url = reverse("maps:utils_index")
    response = admin_client.get(url)

    assert response.status_code == 200


def test_utils_index_trip_list(admin_client):
    trip1 = TripFactory(title="Trip 1")
    trip2 = TripFactory(title="Trip 2")

    url = reverse("maps:utils_index")
    response = admin_client.get(url)
    content = response.content.decode("utf8")

    assert "Trip 1" in content
    assert "Trip 2" in content


# -------------------------------------------------------------------------------------
#                                                                  Donwload Garmin Data
# -------------------------------------------------------------------------------------
def test_download_tcx_func():
    view = resolve("/utils/download_tcx/trip-title/")

    assert views.DownloadTcx == view.func.view_class


def test_download_tcx_index_200(client_logged):
    trip = TripFactory()

    url = reverse("maps:download_tcx", kwargs={"trip": trip.slug})
    response = client_logged.get(url, follow=True)

    assert response.status_code == 200


def test_download_tcx_not_logged(client):
    trip = TripFactory()

    url = reverse("maps:download_tcx", kwargs={"trip": trip.slug})
    response = client.get(url)

    assert response.status_code == 302


# -------------------------------------------------------------------------------------
#                                                                        New Tracks View
# -------------------------------------------------------------------------------------
def test_update_tracks_func():
    view = resolve("/utils/update_tracks/trip-title/")

    assert views.SaveNewTracks == view.func.view_class


def test_update_tracks_index_200(client_logged):
    trip = TripFactory()

    url = reverse("maps:update_tracks", kwargs={"trip": trip.slug})
    response = client_logged.get(url, follow=True)

    assert response.status_code == 200


def test_update_tracks_not_logged(client):
    trip = TripFactory()

    url = reverse("maps:update_tracks", kwargs={"trip": trip.slug})
    response = client.get(url)

    assert response.status_code == 302


# -------------------------------------------------------------------------------------
#                                                               Rewrite All Tracks View
# -------------------------------------------------------------------------------------
def test_update_all_tracks_func():
    view = resolve("/utils/update_all_tracks/trip-title/")

    assert views.RewriteAllTracks == view.func.view_class


def test_update_all_tracks_index_200(client_logged):
    trip = TripFactory()

    url = reverse("maps:update_all_tracks", kwargs={"trip": trip.slug})
    response = client_logged.get(url, follow=True)

    assert response.status_code == 200


def test_update_all_tracks_not_logged(client):
    trip = TripFactory()

    url = reverse("maps:update_all_tracks", kwargs={"trip": trip.slug})
    response = client.get(url)

    assert response.status_code == 302


# -------------------------------------------------------------------------------------
#                                                                  Login / Logout Views
# -------------------------------------------------------------------------------------
def test_login_func():
    view = resolve("/utils/login/")

    assert views.Login == view.func.view_class


def test_successful_login(client, admin_user):
    url = reverse("maps:login")
    credentials = {"username": "admin", "password": "password"}

    response = client.post(url, credentials, follow=True)

    assert response.status_code == 200
    assert response.context["user"].is_authenticated


def test_login_view_form_fields(client):
    url = reverse("maps:login")
    response = client.get(url)

    actual = response.context["form"].fields
    assert "username" in actual
    assert "password" in actual

    actual = response.content.decode("utf-8")
    assert "username" in actual
    assert "password" in actual


def test_login_view_form_errors_no_password(client):
    url = reverse("maps:login")
    response = client.post(url, {"username": "admin", "password": ""})

    assert "Šis laukas yra privalomas." in response.content.decode("utf-8")
    assert "password" in response.context["form"].errors


def test_login_view_form_errors_no_username(client):
    url = reverse("maps:login")
    response = client.post(url, {"username": "", "password": ""})

    assert "Šis laukas yra privalomas." in response.content.decode("utf-8")
    assert "username" in response.context["form"].errors


def test_login_view_wrong_credentials(client):
    url = reverse("maps:login")
    credentials = {"username": "aaaa", "password": "wrong"}

    response = client.post(url, credentials)

    assert not response.context["form"].is_valid()
    assert (
        "Įveskite teisingą vartotojo vardas ir slaptažodį."
        in response.content.decode("utf-8")
    )


def test_redirect_after_successful_login(client, admin_user):
    url = reverse("maps:login")
    credentials = {"username": "admin", "password": "password"}

    response = client.post(url, credentials, follow=True)

    assert response.resolver_match.url_name == "utils_index"


def test_logout_func():
    view = resolve("/utils/logout/")

    assert views.Logout is view.func.view_class


def test_logout_redirect_to_index(admin_client):
    url = reverse("maps:logout")
    response = admin_client.get(url, follow=True)

    assert response.resolver_match.view_name == "maps:trips"
