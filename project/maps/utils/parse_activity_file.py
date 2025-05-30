import contextlib
import json
from pathlib import Path
from typing import Dict


def get_activity_content(file_path: Path) -> Dict:
    """
    Reads the content of an activity file and returns it as a dictionary.
    The file is expected to be in JSON format.
    """
    try:
        return json.loads(file_path.open().read())
    except json.JSONDecodeError:
        return {}


def get_statistic(activity_file: Path) -> Dict:
    activity = get_activity_content(activity_file)

    # old activities have 'movingDuration': None
    total_time = activity.get("movingDuration") or activity.get("duration")

    stats = {
        "start_time": activity.get("startTimeGMT") + " +0000",
        "total_km": float(activity.get("distance")) / 1000,
        "total_time_seconds": float(total_time),
        "avg_speed": float(activity.get("averageSpeed")) * 3.6,
        "max_speed": float(activity.get("maxSpeed")) * 3.6,
        "calories": 0,
        "avg_cadence": None,
        "avg_heart": None,
        "max_heart": None,
        "avg_temperature": None,
        "ascent": float(activity.get("elevationGain")),
        "descent": float(activity.get("elevationLoss")),
    }

    with contextlib.suppress(TypeError, ValueError):
        stats["calories"] = int(activity.get("calories"))

    with contextlib.suppress(TypeError, ValueError):
        stats["min_altitude"] = float(activity.get("minElevation"))

    with contextlib.suppress(TypeError, ValueError):
        stats["max_altitude"] = float(activity.get("maxElevation"))

    with contextlib.suppress(TypeError, ValueError):
        stats["avg_heart"] = float(activity.get("averageHR"))

    with contextlib.suppress(TypeError, ValueError):
        stats["max_heart"] = float(activity.get("maxHR"))

    with contextlib.suppress(TypeError, ValueError):
        stats["avg_cadence"] = float(activity.get("averageBikingCadenceInRevPerMinute"))

    return stats
