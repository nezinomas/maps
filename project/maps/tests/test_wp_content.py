import json
from types import SimpleNamespace

import pytest
from mock import call, patch

from ..utils import wp_content


@pytest.fixture
def trip():
    return SimpleNamespace(blog="Blog_Url", blog_category=6)


@patch("project.maps.utils.wp_content.get_content")
def test_get_all_pages_content_pages_lte_one(mck, trip):
    wp = SimpleNamespace(
        text=json.dumps([{"id": 1}]), headers={"X-wp_content-TotalPages": 1}
    )
    mck.side_effect = [wp]

    actual = wp_content.get_all_pages_content(trip, "some_url")

    assert actual == [{"id": 1}]


@patch("project.maps.utils.wp_content.get_content")
def test_get_all_pages_content_pages_gt_one(mck, trip):
    wp1 = SimpleNamespace(
        text=json.dumps([{"id": 1}]), headers={"X-wp_content-TotalPages": 2}
    )
    wp2 = SimpleNamespace(
        text=json.dumps([{"id": 2}]), headers={"X-wp_content-TotalPages": 2}
    )
    mck.side_effect = [wp1, wp2]

    actual = wp_content.get_all_pages_content(trip, "some_url")

    assert actual == [{"id": 1}, {"id": 2}]


@patch("project.maps.utils.wp_content.get_content")
def test_get_all_pages_content_pages_link_offset(mck, trip):
    wp1 = SimpleNamespace(
        text=json.dumps([{"id": 1}]), headers={"X-wp_content-TotalPages": 2}
    )
    wp2 = SimpleNamespace(
        text=json.dumps([{"id": 2}]), headers={"X-wp_content-TotalPages": 2}
    )
    mck.side_effect = [wp1, wp2]

    wp_content.get_all_pages_content(trip, "some_url")

    expected = [
        call("Blog_Url", "some_url&per_page=100"),
        call("Blog_Url", "some_url&per_page=100&offset=100"),
    ]

    assert mck.call_args_list == expected
