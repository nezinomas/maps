import contextlib
import json
from datetime import datetime

from django.conf import settings
from django.core.cache import cache
from django.core.serializers.json import DjangoJSONEncoder

from .. import models
from ..templatetags.datetime_filter import format_time
from .statistic_service import get_statistic


def cache_timeout(trip):
    current_date = datetime.now().date()

    # If the trip is ongoing, cache for 1 hour; otherwise, cache for 1 day
    return 3600 if trip.start_date <= current_date <= trip.end_date else 86400


def base_context(trip):
    """Builds the base context dictionary for the map view."""
    return {
        "trip": trip,
        "statistic": get_statistic(trip),
        "google_api_key": settings.ENV["GOOGLE_API_KEY"],
        "tracks": {},
    }


def create_stats(track):
    properties = {
        "total_km": 0,
        "date": track.date.strftime("%Y-%m-%d"),
        "time": 0,
        "avg_speed": 0,
        "ascent": 0,
    }

    with contextlib.suppress(Exception):
        properties["total_km"] = round(track.stats.total_km, 1)
        properties["date"] = track.date.strftime("%Y-%m-%d")
        properties["time"] = format_time(track.stats.total_time_seconds)
        properties["avg_speed"] = round(track.stats.avg_speed, 1)
        properties["ascent"] = round(track.stats.ascent, 0)

    return properties


def create_geo_dict(tracks):
    geo = {"type": "FeatureCollection", "features": []}

    for track in tracks:
        # Prepare feature properties
        properties = create_stats(track)

        # Add last point coordinates
        coords = track.path.coords if track.path else []
        last_point = list(coords[-1]) if coords else None
        if last_point:
            properties["last_point"] = last_point[::-1]

        # Create feature
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "LineString",
                "coordinates": track.path.coords if track.path else [],
            },
            "properties": properties,
        }
        geo["features"].append(feature)

    return geo


def create_geo_json(trip):
    tracks = (
        models.Track.objects.filter(trip=trip).order_by("date").select_related("stats")
    )
    return json.dumps(create_geo_dict(tracks), cls=DjangoJSONEncoder)


def create_context(trip):
    context = base_context(trip)

    cache_key = generate_cache_key(trip)

    context["tracks"] = cache.get(cache_key) or set_cache(trip, cache_key)

    return context


def set_cache(trip, cache_key=None):
    geo_data = create_geo_json(trip)

    if not cache_key:
        cache_key = generate_cache_key(trip)

    cache.set(cache_key, geo_data, timeout=cache_timeout(trip))

    return geo_data


def generate_cache_key(trip):
    """
    Generates a unique cache key based on the trip's primary key.
    """
    return f"geojson_{trip.pk}"
