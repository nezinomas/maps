import contextlib
import orjson
import zlib
from datetime import datetime

from django.conf import settings
from django.core.cache import cache

from .. import models
from ..templatetags.datetime_filter import format_time
from .statistic_service import get_statistic


def generate_cache_key(trip):
    """
    Generates a unique cache key based on the trip's primary key.
    """
    return f"geojson_{trip.pk}"


def generate_cache_timeout(trip):
    current_date = datetime.now().date()
    return (
        settings.GEOJSON_CACHE_TIMEOUTS["ongoing_trip"]
        if trip.start_date <= current_date <= trip.end_date
        else settings.GEOJSON_CACHE_TIMEOUTS["past_trip"]
    )


def create_stats(track):
    properties = {
        "total_km": 0,
        "date": track.date.strftime("%Y-%m-%d"),
        "time": 0,
        "avg_speed": 0,
        "ascent": 0,
    }

    with contextlib.suppress(AttributeError, TypeError):
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
    return orjson.dumps(
        create_geo_dict(tracks), option=orjson.OPT_PASSTHROUGH_DATETIME
    ).decode("utf-8")


def set_cache(trip, cache_key=None, cache_timeout=None):
    if not cache_key:
        cache_key = generate_cache_key(trip)

    if cached_data := cache.get(cache_key):
        return zlib.decompress(cached_data).decode("utf-8")

    geo_data = create_geo_json(trip)

    cache.set(
        key=cache_key,
        value=zlib.compress(geo_data.encode("utf-8")),
        timeout=cache_timeout or generate_cache_timeout(trip),
    )

    return geo_data


def create_context(trip):
    return {
        "trip": trip,
        "statistic": get_statistic(trip),
        "google_api_key": settings.ENV["GOOGLE_API_KEY"],
        "tracks": set_cache(trip),
    }
