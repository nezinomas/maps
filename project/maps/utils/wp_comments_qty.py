import datetime as dt
from collections import Counter
from operator import itemgetter

from dateutil.relativedelta import relativedelta

from ..models import CommentQty, Trip
from . import wp_content as wpContent


def count_comments(trip):
    # get all posts id
    link = f"posts?categories={trip.blog_category}&_fields=id,date"
    posts = wpContent.get_all_pages_content(trip, link)

    # return None if  there are no posts for given category
    if not posts:
        return None, None

    # generate post_id list
    post_id_list = list(map(itemgetter('id'), posts))

    # get comments for posts
    link = f'comments?post={",".join(map(str, post_id_list))}&_fields=post'
    comments = wpContent.get_all_pages_content(trip, link)

    # count comments
    arr = list(map(itemgetter('post'), comments))
    counted = dict(Counter(arr))

    # make new list of CommentQty objects for bulk_create_update
    create_or_update = []
    for post in posts:
        post_id = post['id']
        qty = counted.get(post_id, 0)
        date = dt.datetime.strptime(post['date'], "%Y-%m-%dT%H:%M:%S")

        create_or_update.append(
            CommentQty(
                trip=trip,
                post_id=post_id,
                post_date=date.astimezone(dt.timezone.utc),
                qty=qty))

    # return two objects
    # 1 list of CommentsQty objects for create/update
    # 2 list of posts to show in page
    return create_or_update, post_id_list


def push_comments_qty(trip):
    create_or_update, active_posts = count_comments(trip)

    if not create_or_update:
        return

    # create or update
    CommentQty.objects.bulk_update_or_create(
        create_or_update, ['post_date', 'qty'], match_field='post_id')

    # delete obsolete rows
    all_posts = \
        CommentQty.objects \
        .filter(trip=trip) \
        .values_list('post_id', flat=True)

    if diff := list(set(all_posts) - set(active_posts)):
        CommentQty.objects.filter(trip=trip, post_id__in=diff).delete()


def push_comments_qty_for_all_trips():
    trips = Trip.objects.filter(
        end_date__gte=dt.date.today() + relativedelta(months=+3))

    for trip in trips:
        push_comments_qty(trip)
