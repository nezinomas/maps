from os import path

import pytest
from django.conf import settings

from ..factories import UserFactory


@pytest.fixture()
def project_fs(fs):
    fs.create_dir(path.join(settings.MEDIA_ROOT, 'tracks', '1'))
    fs.create_dir(path.join(settings.MEDIA_ROOT, 'points'))

    template = path.join(
        settings.SITE_ROOT,
        'maps',
        'templates',
        'maps',
        '0-points.js'
    )
    fs.create_file(template)


@pytest.fixture()
def client_logged(client):
    UserFactory()

    client.login(username='test', password='test')

    return client
