from django import template

register = template.Library()


@register.filter(name="format_time")
def format_time(value):
    if type(value) is str or value is None:
        return value

    if type(value) is int:
        value = float(value)

    m, s = divmod(value, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)
