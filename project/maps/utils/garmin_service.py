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

from ..models import Trip
from ..utils.common import get_trip


class GarminService:
    def __init__(self, trip: Trip = None):
        self.trip = trip or get_trip()

    def get_data(self) -> List[str]:
        if not self.trip:
            return ["No trip found"]

        # login to garmin connect
        api = self.get_api()
        if not api:
            return ["Error occurred during Garmin Connect communication"]

        # get activities
        activities = self.get_activities(api)
        if not activities:
            return ["Error occurred during getting garmin activities"]

        arr = []
        for activity in activities:
            # filter non cycling activities
            activity_type = activity["activityType"]["typeKey"]
            if all(x not in activity_type.lower() for x in ("biking", "cycling")):
                continue

            # activity start time must be:
            # greater than trip start time and
            # less than trip end time
            time = activity.get("startTimeGMT")
            time = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
            time = time.astimezone(timezone.utc)

            trip_start_date = datetime.combine(
                self.trip.start_date, datetime.min.time(), tzinfo=timezone.utc
            )
            trip_end_date = datetime.combine(
                self.trip.end_date, datetime.min.time(), tzinfo=timezone.utc
            )

            if time < trip_start_date or time > trip_end_date:
                continue

            # activities list for download
            arr.append(activity)

        if not arr:
            return ["Nothing to sync"]

        # download TCX files for all activities
        if err := self.save_files(api, arr):
            return [f"Error occurred during saving tcx file: {err}"]

        return ["Successfully synced data from Garmin Connect"]

    def get_api(self) -> Garmin:
        try:
            api = Garmin(settings.ENV["GARMIN_USER"], settings.ENV["GARMIN_PASS"])

            api.login()
        except (
            GarminConnectConnectionError,
            GarminConnectAuthenticationError,
            GarminConnectTooManyRequestsError,
        ):
            return None

        return api

    def get_activities(self, api: Garmin) -> List[Dict]:
        try:
            activities = api.get_activities(0, 15)  # 0=start, 1=limit
            # activities = api.get_activities_by_date(
            #     startdate="2018-09-14", enddate="2018-11-01"
            # )
        except Exception as e:
            return None

        return activities

    def save_files(self, api: Garmin, activities: List[Dict]) -> str:
        try:
            tracks_folder = Path(settings.MEDIA_ROOT) / "tracks" / str(self.trip.pk)

            if not tracks_folder.exists():
                tracks_folder.mkdir(parents=True, exist_ok=True)

            for activity in activities:
                activity_id = activity["activityId"]

                output_file = tracks_folder / str(activity_id)

                if output_file.exists():
                    continue

                tcx_data = api.download_activity(
                    activity_id, dl_fmt=api.ActivityDownloadFormat.TCX
                )

                with open(output_file, "w") as activity_file:
                    json.dump(activity, activity_file)

                with open(f"{output_file}.tcx", "wb") as tcx_file:
                    tcx_file.write(tcx_data)

        except Exception as err:
            return err
