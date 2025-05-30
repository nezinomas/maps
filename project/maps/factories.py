from datetime import date, datetime, timezone

import factory
from django.contrib.auth.models import User
from django.contrib.gis.geos import LineString

from .models import CommentQty, Track, Trip


class TripFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Trip
        django_get_or_create = ("title",)

    title = "Trip"
    description = "Trip description"
    start_date = date(2022, 1, 1)
    end_date = date(2022, 1, 31)
    blog = "http://www.trip.com"
    blog_category = "666"


class TrackFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Track

    title = factory.Sequence(lambda n: "Track %03d" % n)
    date = datetime(2022, 1, 1, 3, 2, 1, tzinfo=timezone.utc)
    activity_type = "cycling"
    trip = factory.SubFactory(TripFactory)
    path = LineString((1, 2), (3, 4), srid=4326)


class CommentQtyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CommentQty

    post_id = 1
    post_date = datetime(1999, 1, 1, 1, 1, 1, tzinfo=timezone.utc)
    qty = 2
    trip = factory.SubFactory(TripFactory)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = "test"
    password = "test"
    is_active = True
    is_staff = True
    is_superuser = True
    email = "test@test.com"
