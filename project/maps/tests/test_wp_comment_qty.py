import json
from types import SimpleNamespace

import pytest
from mock import call, patch

from ..utils import wp_comments_qty as CQ


@pytest.fixture
def trip():
    return SimpleNamespace(blog='Blog_Url', blog_category=6)


@patch('project.maps.utils.wp_content.get_content')
@patch('project.maps.utils.wp_content.get_posts_ids')
def test_count_comments(mck_ids, mck_content, trip):
    mck_ids.return_value = [1, 2]
    mck_content.return_value = SimpleNamespace(text=json.dumps([{'post': 1}, {'post': 1}]))

    actual = CQ.count_comments(trip)

    assert actual == {1: 2, 2: 0}


@patch('project.maps.utils.wp_content.get_content')
@patch('project.maps.utils.wp_content.get_posts_ids')
def test_count_comments_link(mck_ids, mck_content, trip):
    mck_ids.return_value = [1, 2]
    mck_content.return_value = SimpleNamespace(text=json.dumps([{'post': 1}, {'post': 1}]))

    CQ.count_comments(trip)

    expected = [call('Blog_Url', 'comments?post=1,2&_fields=post')]

    assert mck_content.call_args_list == expected
