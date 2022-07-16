import datetime

from django.db.models import Sum

from .. import models


def get_statistic(trip):
    total_km = 0.0
    total_time = 0.0
    total_ascent = 0.0
    total_descent = 0.0
    context = {}
    try:
        stats = \
            models.Statistic.objects \
            .filter(track__trip__pk=trip.pk) \
            .filter(track__date__range=(trip.start_date, trip.end_date))

        total_km = stats.aggregate(Sum('total_km'))['total_km__sum']
        total_time = stats.aggregate(Sum('total_time_seconds'))['total_time_seconds__sum']
        total_ascent = stats.aggregate(Sum('ascent'))['ascent__sum']
        total_descent = stats.aggregate(Sum('descent'))['descent__sum']
    except:
        pass

    context = {
        'total_km': total_km,
        'total_time': total_time,
        'total_days': ((datetime.date.today() - trip.start_date).days) + 1,
        'total_ascent': total_ascent,
        'total_descent': total_descent,
    }
    return context
