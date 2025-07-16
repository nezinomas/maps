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


def geo_data(tracks):
    # Build GeoJSON in memory if not cached
    geo_json = {"type": "FeatureCollection", "features": []}

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
        geo_json["features"].append(feature)

    # Serialize once
    return json.dumps(geo_json, cls=DjangoJSONEncoder)


def create_context(trip):
    context = base_context(trip)

    cache_key = f"geojson_{trip.pk}"
    geo_json_data = cache.get(cache_key)

    if not geo_json_data:
        geo_json_data = set_cache(trip, cache_key)

    context["tracks"] = geo_json_data

    return context


def set_cache(trip, cache_key):
    tracks = (
        models.Track.objects.filter(trip=trip).order_by("date").select_related("stats")
    )
    geo_json_data = geo_data(tracks)
    _cache_timeout = cache_timeout(trip)
    cache.set(cache_key, geo_json_data, timeout=_cache_timeout)
    return geo_json_data
