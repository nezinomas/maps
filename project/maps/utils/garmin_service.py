import json
import os
from datetime import datetime, timezone
from typing import Dict, List

from django.conf import settings
from garminconnect import (Garmin, GarminConnectAuthenticationError,
                           GarminConnectConnectionError,
                           GarminConnectTooManyRequestsError)

from ..models import Trip
from ..utils.common import get_trip


class GarminService:
    def __init__(self, trip: Trip = None):
        self.trip = get_trip() if not trip else trip

    def get_data(self) -> str:
        if not self.trip:
            return 'No trip found'

        # login to garmin connect
        api = self.get_api()
        if not api:
            return f'Error occurred during Garmin Connect communication'

        # get activities
        activities = self.get_activities(api)
        if not activities:
            return f'Error occurred during getting garmin activities'

        arr = []
        for activity in activities:
            # filter non cycling activities
            activity_type = activity['activityType']['typeKey']
            if not any(x in activity_type.lower() for x in ('biking', 'cycling')):
                continue

            # activity start time must be:
            # greater than trip start time and
            # less than trip end time
            time = activity.get('startTimeGMT')
            time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
            time = time.astimezone(timezone.utc)

            trip_start_date = datetime.combine(
                self.trip.start_date, datetime.min.time(), tzinfo=timezone.utc)
            trip_end_date = datetime.combine(
                self.trip.end_date, datetime.min.time(), tzinfo=timezone.utc)

            if time < trip_start_date or time > trip_end_date:
                continue

            # activities list for download as tcx file
            arr.append(activity)

        if not arr:
            return 'Nothing to sync'

        # download TCX files for all activities
        err = self.save_tcx_file(api, arr)
        if err:
            return f'Error occurred during saving tcx file: {err}'

        return 'Successfully synced data from Garmin Connect'

    def get_api(self) -> Garmin:
        try:
            api = Garmin(
                settings.ENV('GARMIN_USER'),
                settings.ENV('GARMIN_PASS')
            )

            api.login()
        except (
            GarminConnectConnectionError,
            GarminConnectAuthenticationError,
            GarminConnectTooManyRequestsError
        ):
            return

        return api

    def get_activities(self, api: Garmin) -> List[Dict]:
        try:
            activities = api.get_activities(0, 10)  # 0=start, 1=limit
        except Exception:
            return

        return activities

    def get_activity_statistic(self, activity: Dict) -> Dict:
        stats = {
            'start_time': activity.get('startTimeGMT') + ' +0000',
            'total_km': float(activity.get("distance")) / 1000,
            'total_time_seconds': float(activity.get("movingDuration")),
            'avg_speed': float(activity.get("averageSpeed")) * 3.6,
            'max_speed': float(activity.get("maxSpeed")) * 3.6,
            'calories': int(activity.get("calories")),
            'avg_cadence': None,
            'avg_heart': None,
            'max_heart': None,
            'avg_temperature': None,
            'min_altitude': float(activity.get("minElevation")),
            'max_altitude': float(activity.get("maxElevation")),
            'ascent': float(activity.get("elevationGain")),
            'descent': float(activity.get("elevationLoss")),
        }

        try:
            stats['avg_heart'] = float(activity.get("averageHR"))
        except (TypeError, ValueError):
            pass

        try:
            stats['max_heart'] = float(activity.get("maxHR"))
        except (TypeError, ValueError):
            pass

        try:
            stats['avg_cadence'] = float(activity.get("averageBikingCadenceInRevPerMinute"))
        except (TypeError, ValueError):
            pass

        return stats

    def create_activity_statistic_file(self, activity):
        activity_id = activity["activityId"]

        outfile = os.path.join(
            settings.MEDIA_ROOT, 'tracks', f'{activity_id}.sts')

        data = self.get_activity_statistic(activity)

        with open(outfile, "w") as f:
            json.dump(data, f)

    def save_tcx_file(self, api: Garmin, activities: List[Dict]) -> str:
        try:
            for activity in activities:
                activity_id = activity["activityId"]

                output_file = os.path.join(
                    settings.MEDIA_ROOT, 'tracks', f'{activity_id}.tcx')

                if os.path.exists(output_file):
                    continue

                tcx_data = api.download_activity(
                    activity_id, dl_fmt=api.ActivityDownloadFormat.TCX)

                with open(output_file, "wb") as fb:
                    fb.write(tcx_data)

                # create activity statistic file
                self.create_activity_statistic_file(activity)

        except Exception as err:
            return err

