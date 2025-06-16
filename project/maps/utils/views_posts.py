import re
from django.utils.safestring import mark_safe

from . import wp_content
from .. import models


def get_comment_qty(trip: models.Trip, offset: int):
    return (
        models.CommentQty.objects.filter(trip=trip)
        .values("post_id", "qty")
        .order_by("-post_date")[offset : offset + 10]
    )


def get_wordpress_posts(comment_quantities):
    """Fetch WordPress posts based on comment quantities."""
    if not comment_quantities:
        return None, None

    post_ids = [row["post_id"] for row in comment_quantities]
    ids_str = ",".join(map(str, post_ids))
    endpoint = (
        f"posts?include={ids_str}&per_page=100&_fields=id,link,title,date,content"
    )

    try:
        posts = wp_content.get_content(endpoint)
        return posts, None
    except Exception:
        return None, "Kažkas neveikia. Bandykite prisijungti vėliau."


def process_post_content(posts):
    """Process post content, handle modula gallery, and sanitize content."""
    has_modula_gallery = False
    if not posts:
        return has_modula_gallery, posts

    for post in posts:
        cashed_post = post["content"]["rendered"]

        if "modula" in cashed_post:
            has_modula_gallery = True
            cashed_post = re.sub(r'<a class="post-edit-link".*?</a>', "", cashed_post)

        cashed_post = mark_safe(cashed_post)
        post["content"]["rendered"] = cashed_post

    return has_modula_gallery, posts


def create_context(trip, offset):
    comments_qty = get_comment_qty(trip, offset)
    posts, wp_error = get_wordpress_posts(comments_qty)
    has_modula_gallery, posts = process_post_content(posts)

    return {
        "trip": trip,
        "posts": posts,
        "comments_qty": {row["post_id"]: row["qty"] for row in comments_qty}
        if comments_qty
        else {},
        "offset": offset + 10,
        "wp_error": wp_error,
        "modula_gallery": has_modula_gallery,
    }
