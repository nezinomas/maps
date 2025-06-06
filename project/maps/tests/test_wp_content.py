import json
from types import SimpleNamespace

import pytest
from mock import call, patch

from ..utils import wp_content


@pytest.fixture
def trip():
    return SimpleNamespace(blog="Blog_Url", blog_category=6)


@patch("project.maps.utils.wp_content.get_wp_response")
def test_get_all_pages_content_pages_lte_one(mck):
    wp = SimpleNamespace(text=json.dumps([{"id": 1}]), headers={"X-WP-TotalPages": 1})
    mck.side_effect = [wp]

    actual = wp_content.get_all_pages_content("some_url")

    assert actual == [{"id": 1}]


@patch("project.maps.utils.wp_content.get_wp_response")
def test_get_all_pages_content_pages_gt_one(mck):
    wp1 = SimpleNamespace(text=json.dumps([{"id": 1}]), headers={"X-WP-TotalPages": 2})
    wp2 = SimpleNamespace(text=json.dumps([{"id": 2}]), headers={"X-WP-TotalPages": 2})
    mck.side_effect = [wp1, wp2]

    actual = wp_content.get_all_pages_content("some_url")

    assert actual == [{"id": 1}, {"id": 2}]


@patch("project.maps.utils.wp_content.get_wp_response")
def test_get_all_pages_content_pages_link_offset(mck):
    wp1 = SimpleNamespace(text=json.dumps([{"id": 1}]), headers={"X-WP-TotalPages": 2})
    wp2 = SimpleNamespace(text=json.dumps([{"id": 2}]), headers={"X-WP-TotalPages": 2})
    mck.side_effect = [wp1, wp2]

    wp_content.get_all_pages_content("some_url")

    expected = [
        call("some_url&per_page=100"),
        call("some_url&per_page=100&offset=100"),
    ]

    assert mck.call_args_list == expected
