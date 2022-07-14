import functools
import time
from datetime import date

from ..models import Trip


def timer(func):
    @functools.wraps(func)
    def wrap_func(*args, **kwargs):
        start = time.perf_counter()
        return_value = func(*args, **kwargs)
        end = time.perf_counter()
        total = end-start
        print(f'Finished function: {func.__name__} in {total:.4f} sec')
        return return_value
    return wrap_func


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
