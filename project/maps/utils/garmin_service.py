import contextlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List
from django.conf import settings
from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
)

from ..utils.common import get_trip


def create_api():
    api = None

    with contextlib.suppress(
        GarminConnectConnectionError,
        GarminConnectAuthenticationError,
        GarminConnectTooManyRequestsError,
    ):
        api = Garmin(settings.ENV["GARMIN_USER"], settings.ENV["GARMIN_PASS"])
        api.login()

    return api


# Custom exception
class GarminServiceError(Exception):
    pass


class GarminService:
    def __init__(
        self,
        trip = None,
        start_date = None,
        end_date = None,
        activity_types = None,
        api = None
    ):
        self.trip = (
            trip or get_trip()
        )  # Assume get_trip() returns a Trip model instance
        self.start_date = start_date
        self.end_date = end_date
        self.activity_types = activity_types or ["biking", "cycling"]

        self.api = api or create_api()

    def get_data(self) -> str:
        if not self.trip:
            return "No trip found"

        if not self.api:
            return "Error occurred during Garmin Connect communication"

        try:
            activities = self._fetch_activities()
            filtered_activities = self._filter_activities(activities)

            if not filtered_activities:
                return "Nothing to sync"

            self._save_activities(filtered_activities)

            return "Successfully synced data from Garmin Connect"
        except GarminServiceError as e:
            return f"Error: {e}"

    def _fetch_activities(self) -> List[Dict]:
        try:
            if self.start_date and self.end_date:
                return self.api.get_activities_by_date(self.start_date, self.end_date)
            return self.api.get_activities(0, 15)
        except Exception as e:
            raise GarminServiceError(f"Failed to fetch activities: {str(e)}") from e

    def _filter_activities(self, activities: List[Dict]) -> List[Dict]:
        def is_valid_activity(activity: Dict) -> bool:
            # Filter by activity type
            activity_type = activity["activityType"]["typeKey"].lower()
            if all(x not in activity_type for x in self.activity_types):
                return False

            # Skip date filter if start_date and end_date are provided
            if self.start_date and self.end_date:
                return True

            # Filter by trip date range
            try:
                time = datetime.strptime(
                    activity.get("startTimeGMT"), "%Y-%m-%d %H:%M:%S"
                )
                time = time.astimezone(timezone.utc)
                trip_start = datetime.combine(
                    self.trip.start_date, datetime.min.time(), tzinfo=timezone.utc
                )
                trip_end = datetime.combine(
                    self.trip.end_date, datetime.min.time(), tzinfo=timezone.utc
                )
                return trip_start <= time <= trip_end
            except (ValueError, TypeError):
                return False

        return [activity for activity in activities if is_valid_activity(activity)]

    def _save_activities(self, activities: List[Dict]) -> None:
        try:
            tracks_folder = Path(settings.MEDIA_ROOT) / "tracks" / str(self.trip.pk)

            if not tracks_folder.exists():
                tracks_folder.mkdir(parents=True, exist_ok=True)

            for activity in activities:
                activity_id = activity["activityId"]

                output_file = tracks_folder / str(activity_id)
                if output_file.exists():
                    continue

                tcx_data = self.api.download_activity(
                    activity_id, dl_fmt=self.api.ActivityDownloadFormat.TCX
                )

                with open(output_file, "w") as activity_file:
                    json.dump(activity, activity_file)

                with open(f"{output_file}.tcx", "wb") as tcx_file:
                    tcx_file.write(tcx_data)
        except Exception as e:
            raise GarminServiceError(f"Failed to save activities: {e}") from e
