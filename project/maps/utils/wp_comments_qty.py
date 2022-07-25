import datetime as dt
from dateutil.relativedelta import relativedelta

from django.db import transaction

from ..models import Trip, CommentQty

from . import wp_content as wpContent


def _get_wp_content(trip, post_id_dict):
    return wpContent.get_comments(trip, **post_id_dict)


def _count_comments(trip):
    _dict = wpContent.create_post_id_dictionary(trip)
    _wp = _get_wp_content(trip, _dict)

    for item in _wp:
        _id = str(item['post'])

        if _id in _dict:
            _dict[_id] += 1
        else:
            _dict[_id] = 1

    return _dict


def _insert_qty_db(trip, dict):
    for post_id, qty in dict.items():
        obj, created = CommentQty.objects.update_or_create(
            trip_id=trip.pk,
            post_id=post_id,
            defaults={'qty': qty}
        )


def push_post_comment_qty(trip):
    with transaction.atomic():
        _insert_qty_db(trip, _count_comments(trip))


def push_all_comment_qty():
    trips = Trip.objects.filter(
        end_date__gte=dt.date.today() + relativedelta(months=+3))

    for trip in trips:
        push_post_comment_qty(trip)
