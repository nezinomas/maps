from datetime import timedelta

import pytest
from django.core.cache import cache
from django.urls import reverse
from django.utils.timezone import now

from ..factories import StatisticFactory, TripFactory


@pytest.mark.django_db()
def test_map_view_caching_during_trip(client):
    trip = TripFactory(
        title="Trip",
        start_date=now().date() - timedelta(days=10),
        end_date=now().date() + timedelta(days=10),
    )

    StatisticFactory()

    url = reverse("maps:index", kwargs={"trip": trip.slug})

    # Initial load (cache miss)
    response = client.get(url)

    assert response.status_code == 200
    initial_data = response.context["tracks"]  # Access the GeoJSON from context
    expected_cache_key = f"geojson_{trip.slug}"  # Updated key format
    assert cache.get(expected_cache_key) == initial_data  # Check with full key

    # Second load (cache hit)
    response2 = client.get(url)
    assert response2.status_code == 200
    assert response2.context["tracks"] == initial_data  # Same data from cache
