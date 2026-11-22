import json
import logging
import os
import stat

import pytest
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import CommandError
from garminconnect import Garmin, GarminConnectTooManyRequestsError
from mock import Mock, patch

from ..factories import TripFactory
from ..utils import garmin_service
from ..utils.garmin_service import (
    GarminApi,
    GarminService,
    keep_tokens_shared,
    token_file,
)

MODULE = "project.maps.utils.garmin_service"


def mode(path):
    return stat.S_IMODE(os.stat(path).st_mode)


@pytest.fixture
def tokenstore(tmp_path, monkeypatch):
    store = tmp_path / ".garminconnect"
    store.mkdir()
    monkeypatch.setitem(settings.ENV, "GARMIN_TOKEN_STORE", str(store))
    monkeypatch.setitem(settings.ENV, "GARMIN_USER", "user@example.com")
    monkeypatch.setitem(settings.ENV, "GARMIN_PASS", "secret")
    return store


def real_client():
    garmin = Garmin(email="user@example.com", password="secret")
    garmin.client.di_token = "token"
    garmin.client.di_refresh_token = "refresh"
    garmin.client.di_client_id = "client"
    return garmin.client


def test_token_file_for_directory(tokenstore):
    assert token_file(tokenstore) == tokenstore / "garmin_tokens.json"


def test_token_file_for_json_path(tmp_path):
    assert token_file(tmp_path / "x.json") == tmp_path / "x.json"


def test_library_dump_alone_is_owner_only(tokenstore):
    # The reason for keep_tokens_shared: if garminconnect stops forcing 0600,
    # this fails and the wrapper can go.
    client = real_client()

    client.dump(str(tokenstore))

    assert mode(tokenstore / "garmin_tokens.json") == 0o600


def test_dump_leaves_token_group_readable(tokenstore):
    client = real_client()
    keep_tokens_shared(client)

    client.dump(str(tokenstore))

    path = tokenstore / "garmin_tokens.json"
    assert mode(path) == 0o660
    assert json.loads(path.read_text())["di_refresh_token"] == "refresh"


def test_token_refresh_leaves_token_group_readable(tokenstore):
    # A refresh during the run writes through client._persist_tokens().
    client = real_client()
    keep_tokens_shared(client)
    client._tokenstore_path = str(tokenstore)

    client._persist_tokens()

    assert mode(tokenstore / "garmin_tokens.json") == 0o660


def test_saved_token_is_loaded_back(tokenstore):
    writer = real_client()
    keep_tokens_shared(writer)
    writer.dump(str(tokenstore))

    reader = Garmin(email="user@example.com", password="secret").client
    reader.load(str(tokenstore))

    assert reader.di_token == "token"


@patch(f"{MODULE}.Garmin")
def test_create_api_resumes_from_token_store(mck_garmin, tokenstore):
    api = GarminApi()

    mck_garmin.return_value.login.assert_called_once_with(str(tokenstore))
    assert api._api is mck_garmin.return_value
    assert bool(api)


@patch(f"{MODULE}.keep_tokens_shared")
@patch(f"{MODULE}.Garmin")
def test_create_api_shares_tokens_before_login(mck_garmin, mck_share, tokenstore):
    calls = []
    mck_share.side_effect = lambda client: calls.append("share")
    mck_garmin.return_value.login.side_effect = lambda path: calls.append("login")

    GarminApi()

    mck_share.assert_called_once_with(mck_garmin.return_value.client)
    assert calls == ["share", "login"]


@patch(f"{MODULE}.Garmin")
def test_create_api_rate_limited_is_logged(mck_garmin, tokenstore, caplog):
    mck_garmin.return_value.login.side_effect = GarminConnectTooManyRequestsError(
        "Too many login attempts"
    )

    with caplog.at_level(logging.WARNING, logger=MODULE):
        api = GarminApi()

    assert not api
    assert "Garmin login failed: Too many login attempts" in caplog.text


@patch(f"{MODULE}.Garmin")
def test_unreadable_token_is_logged(mck_garmin, tokenstore, caplog, monkeypatch):
    (tokenstore / "garmin_tokens.json").write_text("{}")
    monkeypatch.setattr(garmin_service.os, "access", lambda path, how: False)

    with caplog.at_level(logging.WARNING, logger=MODULE):
        GarminApi()

    assert "is not readable by this user" in caplog.text


@patch(f"{MODULE}.Garmin")
def test_readable_token_is_not_logged(mck_garmin, tokenstore, caplog):
    (tokenstore / "garmin_tokens.json").write_text("{}")

    with caplog.at_level(logging.WARNING, logger=MODULE):
        GarminApi()

    assert "not readable" not in caplog.text


@patch(f"{MODULE}.Garmin")
def test_service_reports_failed_login(mck_garmin, tokenstore):
    mck_garmin.return_value.login.side_effect = GarminConnectTooManyRequestsError(
        "429"
    )

    actual = GarminService(trip=TripFactory.build()).get_data()

    assert actual == "Error occurred during Garmin Connect communication"


@patch("project.maps.management.commands.get_data.GarminService")
def test_get_data_command_fails_on_error_result(mck_service):
    mck_service.return_value.get_data.return_value = (
        "Error occurred during Garmin Connect communication"
    )

    with pytest.raises(CommandError, match="Garmin Connect communication"):
        call_command("get_data")


@patch("project.maps.management.commands.get_data.GarminService")
def test_get_data_command_nothing_to_sync_is_success(mck_service, capsys):
    mck_service.return_value.get_data.return_value = "Nothing to sync"

    call_command("get_data")

    assert "successfully synced" in capsys.readouterr().out
