from os import path

import pytest
from django.conf import settings
from django.db.models.signals import post_delete, post_save

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


@pytest.fixture(autouse=True)  # Automatically use in tests.
def mute_signals(request):
    # Skip applying, if marked with `enabled_signals`
    if 'enable_signals' in request.keywords:
        return

    signals = [
        post_save,
        post_delete,
    ]
    restore = {}
    for signal in signals:
        # Temporally remove the signal's receivers (a.k.a attached functions)
        restore[signal] = signal.receivers
        signal.receivers = []

    def restore_signals():
        # When the test tears down, restore the signals.
        for signal, receivers in restore.items():
            signal.receivers = receivers

    # Called after a test has finished.
    request.addfinalizer(restore_signals)
