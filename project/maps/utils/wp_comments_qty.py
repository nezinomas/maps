import datetime as dt
from dateutil.relativedelta import relativedelta

from django.db import transaction

from ..models import Trip, CommentQty

from . import wp_content as wpContent


def _count_comments(trip):
    posts = wpContent.get_posts(trip)
    arr = {post.get('id'): 0 for post in posts}
    comments = wpContent.get_comments(trip, arr.keys())

    for comment in comments:
        post_id = comment.get('post')
        arr[post_id] += 1

    return arr


def _insert_qty_db(trip, dict):
    for post_id, qty in dict.items():
        _, _ = CommentQty.objects.update_or_create(
            trip_id=trip.pk,
            post_id=post_id,
            defaults={'qty': qty}
        )


def push_post_comment_qty(trip):
    with transaction.atomic():
        comments = _count_comments(trip)

        _insert_qty_db(trip, comments)


def push_all_comment_qty():
    trips = Trip.objects.filter(
        end_date__gte=dt.date.today() + relativedelta(months=+3))

    for trip in trips:
        push_post_comment_qty(trip)
