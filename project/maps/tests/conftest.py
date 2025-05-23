from os import path

import pytest
from django.conf import settings
from django.db.models.signals import post_delete, post_save

from ..factories import UserFactory


@pytest.fixture()
def project_fs(fs):
    fs.create_dir(path.join(settings.MEDIA_ROOT, "tracks", "1"))


@pytest.fixture()
def client_logged(client):
    UserFactory()

    client.login(username="test", password="test")

    return client
