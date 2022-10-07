import json
from types import SimpleNamespace

import pytest
from mock import call, patch

from ..utils import wp_content as WP


@pytest.fixture
def trip():
    return SimpleNamespace(blog='url', blog_category=6)


@patch('project.maps.utils.wp_content.get_content')
def test_get_posts_ids_pages_lte_one(mck, trip):
    wp = SimpleNamespace(text=json.dumps([{'id': 1}]), headers={'X-WP-TotalPages': 1})
    mck.side_effect = [wp]

    actual = WP.get_posts_ids(trip)

    assert actual == [1]


@patch('project.maps.utils.wp_content.get_content')
def test_get_posts_ids_pages_gt_one(mck, trip):
    wp1 = SimpleNamespace(text=json.dumps([{'id': 1}]), headers={'X-WP-TotalPages': 2})
    wp2 = SimpleNamespace(text=json.dumps([{'id': 2}]), headers={'X-WP-TotalPages': 2})
    mck.side_effect = [wp1, wp2]

    actual = WP.get_posts_ids(trip)

    assert actual == [1, 2]


@patch('project.maps.utils.wp_content.get_content')
def test_get_posts_ids_pages_link_offset(mck, trip):
    wp1 = SimpleNamespace(text=json.dumps([{'id': 1}]), headers={'X-WP-TotalPages': 2})
    wp2 = SimpleNamespace(text=json.dumps([{'id': 2}]), headers={'X-WP-TotalPages': 2})
    mck.side_effect = [wp1, wp2]

    WP.get_posts_ids(trip)

    expected = [
        call('url', 'posts?categories=6&_fields=id&per_page=100'),
        call('url', 'posts?categories=6&_fields=id&per_page=100&offset=100')
    ]

    assert mck.call_args_list == expected
