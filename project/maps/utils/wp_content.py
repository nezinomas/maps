import json
from typing import Dict

import requests
from django.conf import settings
from wordpress import API


def get_wp_response(link_end):
    # wpapi = API(
    #     url=blog_url,
    #     consumer_key=settings.ENV["CONSUMER_KEY"],
    #     consumer_secret=settings.ENV["CONSUMER_SECRET"],
    #     api="wp-json",
    #     version="wp/v2",
    #     wp_user=settings.ENV["WP_USER"],
    #     wp_pass=settings.ENV["WP_PASS"],
    #     oauth1a_3leg=True,
    #     creds_store="",
    #     callback=f"{settings.ENV['WP_BLOG_URL']}/oauth1_callback",
    # )

    # return wpapi.get(link_end)

    link = f"{settings.ENV['WP_BLOG_URL']}/wp-json/wp/v2/{link_end}"
    return requests.get(link)


def get_content(link: str) -> Dict:
    response = get_wp_response(link)
    return json.loads(response.text)


def get_all_pages_content(link):
    per_page = 100
    link = f"{link}&per_page={per_page}"

    response = get_wp_response(link)
    content = json.loads(response.text)
    pages = int(response.headers["X-WP-TotalPages"])

    if pages > 1:
        for page in range(1, pages):
            link_offset = f"{link}&offset={page * per_page}"
            content += get_content(link_offset)

    return content
