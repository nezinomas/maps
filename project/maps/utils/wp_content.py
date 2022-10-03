import json

from wordpress import API
from django.conf import settings


def get_content(blog_url, link_end):
    wpapi = API(
        url=blog_url,
        consumer_key=settings.ENV("CONSUMER_KEY"),
        consumer_secret=settings.ENV("CONSUMER_SECRET"),
        api="wp-json",
        version="wp/v2",
        wp_user=settings.ENV("WP_USER"),
        wp_pass=settings.ENV("WP_PASS"),
        oauth1a_3leg=True,
        creds_store="",
        callback=f'{blog_url}/oauth1_callback'
    )

    r = wpapi.get(link_end)

    return json.loads(r.text)


def get_posts(trip):
    link = f"posts?categories={trip.blog_category}&per_page=70"

    return get_content(trip.blog, link)


def get_comments(trip, posts_id_arr):
    link = f'comments?post={",".join(map(str, posts_id_arr))}'

    return get_content(trip.blog, link)


def get_comment_qty(trip):
    comments = trip.comment_qty.all().values('post_id', 'qty')

    return {comment['post_id']: comment['qty'] for comment in comments}
