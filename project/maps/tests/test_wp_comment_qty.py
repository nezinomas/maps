from datetime import datetime, timezone

import pytest
from mock import call, patch

from ..factories import CommentQtyFactory, TripFactory
from ..models import CommentQty
from ..utils import wp_comments_qty as CQ

pytestmark = pytest.mark.django_db


@patch('project.maps.utils.wp_content.get_all_pages_content')
def test_count_comments(mck_content):
    trip = TripFactory.build()

    posts = [{'id': 1, 'date': '1999-01-01T03:01:01'}]
    comments = [{'post': 1}, {'post': 1}]
    mck_content.side_effect = [posts, comments]

    create_or_update, post_id_list = CQ.count_comments(trip)

    assert (len(create_or_update)) == 1
    assert create_or_update[0].trip.title == 'Trip'
    assert create_or_update[0].post_id == 1
    assert create_or_update[0].post_date == datetime(1999, 1, 1, 1, 1, 1, tzinfo=timezone.utc)
    assert create_or_update[0].qty == 2

    assert post_id_list == [1]


@patch('project.maps.utils.wp_content.get_all_pages_content')
def test_count_comments_no_posts(mck_content):
    trip = TripFactory.build()

    posts = []
    mck_content.side_effect = [posts]

    create_or_update, post_id_list = CQ.count_comments(trip)

    assert create_or_update is None
    assert post_id_list is None
    assert mck_content.call_count == 1


@patch('project.maps.utils.wp_content.get_all_pages_content')
def test_count_comments_no_comments(mck_content):
    trip = TripFactory.build()

    posts = [{'id': 1, 'date': '1999-01-01T03:01:01'}]
    comments = []
    mck_content.side_effect = [posts, comments]

    create_or_update, post_id_list = CQ.count_comments(trip)

    assert (len(create_or_update)) == 1
    assert create_or_update[0].trip.title == 'Trip'
    assert create_or_update[0].post_id == 1
    assert create_or_update[0].post_date == datetime(1999, 1, 1, 1, 1, 1, tzinfo=timezone.utc)
    assert create_or_update[0].qty == 0

    assert post_id_list == [1]


@patch('project.maps.utils.wp_content.get_all_pages_content')
def test_count_comments_link(mck_content):
    trip = TripFactory.build()

    posts = [{'id': 1, 'date': '1999-01-01T03:01:01'}]
    comments = [{'post': 1}, {'post': 1}]
    mck_content.side_effect = [posts, comments]

    CQ.count_comments(trip)

    expected = [
        call(trip, 'posts?categories=666&_fields=id,date'),
        call(trip, 'comments?post=1&_fields=post')
    ]

    assert mck_content.call_args_list == expected


@patch('project.maps.utils.wp_comments_qty.count_comments')
def test_push_comments_new_record(mck):
    trip = TripFactory()
    create_or_update = [CommentQtyFactory.build(trip=trip)]
    post_id = [1]
    mck.return_value = (create_or_update, post_id)

    CQ.push_comments_qty(trip)
    actual = CommentQty.objects.all()

    assert actual.count() == 1
    assert actual[0].post_date == datetime(1999, 1, 1, 1, 1, 1, tzinfo=timezone.utc)
    assert actual[0].qty == 2


@patch('project.maps.utils.wp_comments_qty.count_comments')
def test_push_comments_update_qty_and_date(mck):
    CommentQtyFactory()
    trip = TripFactory()
    create_or_update = [CommentQtyFactory.build(
            trip=trip,
            post_id=1,
            post_date=datetime(2000, 1, 1, 1, 1, 1, tzinfo=timezone.utc),
            qty=3)]
    post_id = [1]
    mck.return_value = (create_or_update, post_id)

    CQ.push_comments_qty(trip)
    actual = CommentQty.objects.all()

    assert actual.count() == 1
    assert actual[0].post_date == datetime(2000, 1, 1, 1, 1, 1, tzinfo=timezone.utc)
    assert actual[0].qty == 3


@patch('project.maps.utils.wp_comments_qty.count_comments')
def test_push_comments_update_delete_old_post_id(mck):
    trip = TripFactory()
    obj = CommentQtyFactory()
    obj_old = CommentQtyFactory(post_id=2)

    mck.return_value = ([obj], [1])

    CQ.push_comments_qty(trip)
    actual = CommentQty.objects.all()

    assert actual.count() == 1
    assert actual[0].post_id == obj.post_id
