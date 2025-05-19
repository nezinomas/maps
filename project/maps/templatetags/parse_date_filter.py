from dateutil.parser import parse
from django import template

register = template.Library()


@register.filter(name="parse_date")
def parse_date(date_string):
    try:
        d = date_string.replace("T", " ")
        return parse(d)
    except ValueError:
        return None
