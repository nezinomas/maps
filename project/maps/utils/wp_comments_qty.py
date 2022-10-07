import datetime as dt

from dateutil.relativedelta import relativedelta
from django.db import transaction

from ..models import CommentQty, Trip
from . import wp_content as wpContent


def count_comments(trip):
    posts = wpContent.get_posts_ids(trip)
    arr = {post: 0 for post in posts}

    link = f'comments?post={",".join(map(str, posts))}&_fields=post'
    comments = wpContent.get_json(trip.blog, link)

    for comment in comments:
        post_id = comment.get('post')
        arr[post_id] += 1

    return arr


def push_comments_qty(trip):
    with transaction.atomic():
        comments = count_comments(trip)

        for post_id, qty in comments.items():
            CommentQty.objects.update_or_create(
                trip_id=trip.pk,
                post_id=post_id,
                defaults={'qty': qty}
            )


def push_comments_qty_for_all_trips():
    trips = Trip.objects.filter(
        end_date__gte=dt.date.today() + relativedelta(months=+3))

    for trip in trips:
        push_comments_qty(trip)
