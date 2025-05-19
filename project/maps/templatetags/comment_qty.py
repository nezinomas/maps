from django import template

register = template.Library()


@register.simple_tag(name="comment_qty")
def comment_qty(dict, post_id):
    qty = 0

    if post_id in dict:
        qty = dict[post_id]

    return qty
