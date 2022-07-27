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
    return get_content(
        trip.blog,
        f"posts?categories={trip.blog_category}&per_page=70")


def create_post_id_dictionary(trip):
    posts = get_posts(trip)

    return {str(post['id']): 0 for post in posts}


def post_link(arg):
    return f'&post={arg}'


def create_comment_rest_link(*args, **kwargs):
    _post_link = ''

    if args:
        _post_link += ''.join([post_link(arg) if arg else '' for arg in args])

    if kwargs:
        _post_link += ''.join([post_link(key) for key in kwargs.keys()])

    return f'comments?per_page=100{_post_link}'


def get_comments(trip, *args, **kwargs):
    # comments?post=7363&post=7352&per_page=100'
    link = create_comment_rest_link(*args, **kwargs)

    return get_content(trip.blog, link)


def get_comment_qty(trip):
    comments = trip.comment_qty.all().values('post_id', 'qty')

    return {comment['post_id']: comment['qty'] for comment in comments}
