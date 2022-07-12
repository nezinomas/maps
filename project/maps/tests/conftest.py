from os import path

import pytest
from django.conf import settings

from ..factories import UserFactory


@pytest.fixture(autouse=True)
def create_folders_in_fake_filesystem(fs):
    fs.create_dir(path.join(settings.MEDIA_ROOT, 'tracks'))
    fs.create_dir(path.join(settings.MEDIA_ROOT, 'points'))

    template = path.join(settings.SITE_ROOT, 'maps', 'templates', 'maps', '0-points.js')
    fs.create_file(template)


@pytest.fixture()
def client_logged(client):
    UserFactory()

    client.login(username='test', password='test')

    return client
