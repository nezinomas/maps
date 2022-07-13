from datetime import date

from ..models import Trip


def get_trip() -> Trip:
    today = date.today()

    try:
        trip = \
            Trip.objects \
            .filter(start_date__lte=today, end_date__gte=today) \
            .order_by('id') \
            .latest('id')
    except Trip.DoesNotExist:
        return None

    return trip
