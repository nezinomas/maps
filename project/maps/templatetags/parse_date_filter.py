from django import template
from dateutil.parser import parse

register = template.Library()


@register.filter(name='parse_date')
def parse_date(date_string):
    try:
        d = date_string.replace('T', ' ')
        return parse(d)
    except ValueError:
        return None
