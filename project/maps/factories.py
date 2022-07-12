from datetime import date, datetime

import factory
from django.contrib.auth.models import User

from .models import Point, Track, Trip


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


class PointFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Point

    latitude = 11.11
    longitude = 22.22
    altitude = 33.33
    distance_meters = 44.44
    datetime = datetime(2022, 1, 1, 3, 2, 1)

    track = factory.SubFactory(TrackFactory)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = 'test'
    password = 'test'
    is_active = True
    is_staff = True
    is_superuser = True
    email = 'test@test.com'
