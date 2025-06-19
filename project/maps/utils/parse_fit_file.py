import itertools as it
from datetime import datetime

import fitdecode
from django.contrib.gis.geos import LineString
from django.utils import timezone
from parser import parse_coordinates, parse_timestamp


def get_track_path(fit_file_path):
    try:
        return LineString(parse_coordinates(str(fit_file_path)))
    except Exception as e:
        print(f"Something wrong with rust parser: {e}")
        return parse_coordinates_pyton(fit_file_path)


def get_track_date(fit_file_path):
    try:
        return parse_timestamp(str(fit_file_path))
    except Exception as e:
        print(f"Something wrong with rust parser: {e}")
        return parse_timestamp_pyton(fit_file_path)


def parse_coordinates_pyton(fit_file_path):
    coordinates = []

    try:
        with fitdecode.FitReader(fit_file_path) as fit:
            records = it.filterfalse(
                lambda f: (
                    f.frame_type != fitdecode.FIT_FRAME_DATA
                    or f.name != "record"
                    or not all(
                        f.has_field(field)
                        for field in ("position_lat", "position_long")
                    )
                ),
                fit,
            )

            # Convert semicircles to degrees rounded to 5 decimals
            #  using map for speed
            to_deg = lambda x: round(x * (180.0 / 2**31), 5)
            coordinates = list(
                zip(
                    map(
                        to_deg,
                        (frame.get_value("position_long") for frame in records),
                    ),
                    map(
                        to_deg,
                        (frame.get_value("position_lat") for frame in records),
                    ),
                )
            )

            return LineString(coordinates, srid=4326)

    except Exception:
        return None


def parse_timestamp_pyton(fit_file_path):
    def get_timestamp(frame):
        """Helper to extract timestamp from a frame."""
        if frame.name in ("file_id", "session"):
            return frame.get_value("time_created") or frame.get_value("start_time")
        return frame.get_value("timestamp") if frame.name == "record" else None

    try:
        with fitdecode.FitReader(fit_file_path) as fit:
            for frame in fit:
                if frame.frame_type != fitdecode.FIT_FRAME_DATA:
                    continue
                timestamp = get_timestamp(frame)
                if timestamp and isinstance(timestamp, datetime):
                    return timestamp
            return datetime.now(timezone.utc)

    except Exception:
        return datetime.now(timezone.utc)
