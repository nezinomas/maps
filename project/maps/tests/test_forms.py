from datetime import date

import pytest

from .. import forms, models
from ..factories import TripFactory

pytestmark = pytest.mark.django_db


def test_trip_form():
    forms.TripForm()


def test_trip_form_fields():
    form = forms.TripForm().as_p()

    assert '<input type="text" name="title"' in form
    assert '<textarea name="description"' in form
    assert '<input type="number" name="blog_category"' in form
    assert '<input type="text" name="start_date"' in form
    assert '<input type="text" name="end_date"' in form


def test_trip_form_title_is_not_valid():
    form = forms.TripForm(
        data={
            "title": None,
            "description": None,
            "blog_category": 1,
            "start_date": "1999-1-1",
            "end_date": "1999-12-31",
        }
    )

    assert not form.is_valid()
    assert "title" in form.errors


def test_trip_form_title_is_not_valid_and_has_is_invalid_css_class():
    form = forms.TripForm(
        data={
            "title": None,
            "description": None,
            "blog_category": 1,
            "start_date": "1999-1-1",
            "end_date": "1999-12-31",
        }
    )

    assert not form.is_valid()
    assert "title" in form.errors
    assert 'class="is-invalid"' in form.as_p()


def test_trip_form_blog_category_is_not_valid():
    form = forms.TripForm(
        data={
            "title": "Trip",
            "description": None,
            "blog_category": None,
            "start_date": "1999-1-1",
            "end_date": "1999-12-31",
        }
    )

    assert not form.is_valid()
    assert "blog_category" in form.errors


@pytest.mark.parametrize(
    "dt",
    [("x"), (None), ("1999.1.1"), ("1999-1")],
)
def test_trip_form_start_date_is_not_valid(dt):
    form = forms.TripForm(
        data={
            "title": "Trip",
            "description": None,
            "blog_category": 1,
            "start_date": dt,
            "end_date": "1999-12-31",
        }
    )

    assert not form.is_valid()
    assert len(form.errors) == 1
    assert "start_date" in form.errors


@pytest.mark.parametrize(
    "dt",
    [("x"), (None), ("1999.1.1"), ("1999-1")],
)
def test_trip_form_end_date_is_not_valid(dt):
    form = forms.TripForm(
        data={
            "title": "Trip",
            "description": None,
            "blog_category": 1,
            "start_date": "1999-1-1",
            "end_date": dt,
        }
    )

    assert not form.is_valid()
    assert len(form.errors) == 1
    assert "end_date" in form.errors


def test_trip_form_end_date_earlier_than_start_date():
    form = forms.TripForm(
        data={
            "title": "Trip",
            "description": None,
            "blog_category": 1,
            "start_date": "1999-1-1",
            "end_date": "1998-1-1",
        }
    )

    assert not form.is_valid()
    assert len(form.errors) == 1
    assert "end_date" in form.errors


def test_trip_form_dates_valid():
    form = forms.TripForm(
        data={
            "title": "Trip",
            "description": None,
            "blog_category": 1,
            "start_date": "1999-1-1",
            "end_date": "1999-12-31",
        }
    )

    assert form.is_valid()


def test_trip_form_save_with_valid_data():
    form = forms.TripForm(
        data={
            "title": "Trip",
            "description": "Description",
            "blog_category": 1,
            "start_date": "1999-1-1",
            "end_date": "1999-12-31",
        }
    )

    assert form.is_valid()

    form.save()

    actual = models.Trip.objects.first()

    assert actual.title == "Trip"
    assert actual.slug == "trip"
    assert actual.description == "Description"
    assert actual.blog_category == "1"
    assert actual.start_date == date(1999, 1, 1)
    assert actual.end_date == date(1999, 12, 31)


def test_trip_form_unique_slug_for_same_trip_title():
    TripFactory()

    form = forms.TripForm(
        data={
            "title": "Trip",
            "description": "Description",
            "blog_category": 1,
            "start_date": "1999-1-1",
            "end_date": "1999-12-31",
        }
    )

    assert form.is_valid()

    form.save()

    actual = models.Trip.objects.last()

    assert actual.title == "Trip"
    assert actual.slug == "trip-1"
    assert actual.description == "Description"
    assert actual.blog_category == "1"
    assert actual.start_date == date(1999, 1, 1)
    assert actual.end_date == date(1999, 12, 31)