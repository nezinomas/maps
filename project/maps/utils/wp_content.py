import json
from typing import Dict

from django.conf import settings
from wordpress import API


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

    return wpapi.get(link_end)


def get_json(blog_url: str, link: str) -> Dict:
    response = get_content(blog_url, link)
    return json.loads(response.text)


def get_all_pages_content(trip, link):
    response = get_content(trip.blog, link)
    content = json.loads(response.text)
    pages = int(response.headers['X-WP-TotalPages'])

    if pages > 1:
        for page in range(1, pages):
            link_offset = f'{link}&offset={page * 100}'
            response = get_content(trip.blog, link_offset)
            content += json.loads(response.text)

    return content


def get_posts_ids(trip):
    link = f"posts?categories={trip.blog_category}&_fields=id&per_page=100"
    content = get_all_pages_content(trip, link)

    return [x['id'] for x in content]
