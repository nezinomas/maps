import datetime as dt

from dateutil.relativedelta import relativedelta
from django.db import transaction

from ..models import CommentQty, Trip
from . import wp_content as wpContent


def count_comments(trip):
    # get all posts id
    link = f"posts?categories={trip.blog_category}&_fields=id"
    posts = wpContent.get_all_pages_content(trip, link)
    arr = {post['id']: 0 for post in posts}

    # get comments for posts
    link = f'comments?post={",".join(map(str, arr.keys()))}&_fields=post'
    comments = wpContent.get_all_pages_content(trip, link)

    # count comments
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
