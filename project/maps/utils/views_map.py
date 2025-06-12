import json
from datetime import datetime

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder

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


def geo_data(tracks):
    # Build GeoJSON in memory if not cached
    geo_json = {"type": "FeatureCollection", "features": []}

    for track in tracks:
        # Prepare feature properties
        properties = {
            "total_km": round(track.stats.total_km, 2)
            if hasattr(track.stats, "total_km")
            else 0,
            "date": track.date.strftime("%Y-%m-%d"),
            "time": format_time(getattr(track.stats, "total_time_seconds", 0)),
            "avg_speed": round(getattr(track.stats, "avg_speed", 0), 1),
            "ascent": getattr(track.stats, "ascent", 0),
        }

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
