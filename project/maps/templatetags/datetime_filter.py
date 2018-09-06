from django import template
from datetime import date, timedelta, time

register = template.Library()

@register.filter(name='format_datetime')
def format_datetime(value):
    if type(value) == str or value == None:
        return value

    if type(value) == int:
        value = float(value)

    m, s = divmod(value, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)
    # return time(h, m, s)
