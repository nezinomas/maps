import json

from wordpress import API

from ...config.secrets import get_secret


def get_content(blog_url, link_end):
    wpapi = API(
        url=blog_url,
        consumer_key=get_secret("CONSUMER_KEY"),
        consumer_secret=get_secret("CONSUMER_SECRET"),
        api="wp-json",
        version="wp/v2",
        wp_user=get_secret("WP_USER"),
        wp_pass=get_secret("WP_PASS"),
        oauth1a_3leg=True,
        creds_store="",
        callback='{}/oauth1_callback'.format(blog_url)
    )

    r = wpapi.get(link_end)

    return json.loads(r.text)


def get_posts(trip):
    return get_content(
        trip.blog,
        "posts?categories={}&per_page=70".format(
            trip.blog_category)
    )


def create_post_id_dictionary(trip):
    posts = get_posts(trip)

    dict = {}
    for post in posts:
        dict[post['id']] = 0

    return dict


def create_comment_rest_link(post_id_dict):
    _str = ''
    if post_id_dict:
        for id in post_id_dict:
            _str += '&post={}'.format(id)

    return 'comments?per_page=100{}'.format(_str)


def get_comments(trip, post_id_dict):
    # comments?post=7363&post=7352&per_page=100'
    link = create_comment_rest_link(post_id_dict)

    return get_content(trip.blog, link)


def get_comment_qty(trip):
    qty = {}

    _list = trip.comment_qty.all().values('post_id', 'qty')

    for i in _list:
        qty[i['post_id']] = i['qty']

    return qty
