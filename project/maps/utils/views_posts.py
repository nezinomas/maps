import re
from typing import Dict, List, Optional, Tuple

from django.db.models import QuerySet
from django.utils.safestring import mark_safe

from . import wp_content
from .. import models


def get_post_comment_map(trip: models.Trip, offset: int) -> QuerySet:
    return (
        models.CommentQty.objects.filter(trip=trip)
        .values("post_id", "qty")
        .order_by("-post_date")[offset:offset + 10]
    )


def get_posts(trip, offset):
    posts = None
    wp_error = False

    if qs := get_post_comment_map(trip, offset):
        comments_qty = {row["post_id"]: row["qty"] for row in qs}
        ids = ",".join(map(str, comments_qty.keys()))
        link = f"posts?include={ids}&per_page=100&_fields=id,link,title,date,content"

        try:
            posts = wp_content.get_content(link)
        except Exception:
            wp_error = "Kažkas neveikia. Bandykite prisijungti vėliau."

    return posts, wp_error

def create_context(trip, offset):
    modula_gallery = False
    comments_qty = {}

    posts, wp_error = get_posts (trip, offset)

    if posts:
        for post in posts:
            cashed_post = post["content"]["rendered"]

            if "modula" in cashed_post:
                modula_gallery = True
                cashed_post = re.sub(
                    r'<a class="post-edit-link".*?</a>', "", cashed_post
                )

            cashed_post = mark_safe(cashed_post)
            post["content"]["rendered"] = cashed_post

    return {
        "trip": trip,
        "posts": posts,
        "comments_qty": comments_qty,
        "offset": offset + 10,
        "wp_error": wp_error,
        "modula_gallery": modula_gallery,
    }
