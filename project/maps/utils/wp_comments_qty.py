from django.db import transaction

from ..models import CommentQty

from . import wp_content as wpContent


def _count_comments(trip):
    dict = {}
    wp = wpContent.get_all_comments(trip)

    for item in wp:
        id = item['post']

        if id in dict:
            dict[id] += 1
        else:
            dict[id] = 1

    return dict


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
