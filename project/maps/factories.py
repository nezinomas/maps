from datetime import date, datetime
from decimal import Decimal

import factory

from .models import CommentQty, Point, Statistic, Track, Trip


class TripFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Trip
        django_get_or_create = ('title',)

    title = 'Trip'
    description = 'Trip description'
    start_date = date(2022, 1, 1)
    end_date = date(2022, 1, 31)
    blog = 'http://www.trip.com'
    blog_category = '666'


class TrackFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Track

    title = '999'
    date = datetime(2022, 1, 1, 3, 2, 1)
    activity_type = 'cycling'
    trip = factory.SubFactory(TripFactory)
