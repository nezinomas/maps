import os
from datetime import date, datetime
from typing import Dict, List

from django.conf import settings
from garminconnect import (Garmin, GarminConnectAuthenticationError,
                           GarminConnectConnectionError,
                           GarminConnectTooManyRequestsError)

from ..models import Statistic, Track, Trip


def get_data() -> str:
    try:
        api = get_api()
    except (
        GarminConnectConnectionError,
        GarminConnectAuthenticationError,
        GarminConnectTooManyRequestsError
    ) as err:
        return(f'Error occurred during Garmin Connect communication: {err}')

    try:
        activities = get_activities(api)
    except Exception as err:
        return(f'Error occurred during getting garmin activities: {err}')

    # filter non cycling activities
    activities = filter_non_cycling_activities(activities)
    if not activities:
        return('No cycling activities found')

    # get current trip
    try:
        trip = \
            Trip.objects \
            .filter(end_date__gte=date.today()) \
            .order_by('id') \
            .latest('id')
    except Trip.DoesNotExist:
        return('No trip found')

    # download TCX files for all activities
    try:
        save_tcx_file(api, activities)
    except Exception as err:
        return(f'Error occurred during saving tcx file: {err}')

    # get all tracks for current trip
    tracks = \
        Track.objects \
        .filter(trip=trip) \
        .values_list('title', flat=True)

    # create tracks and statistic for all activities
    for activity in activities:
        track = create_track(trip, activity, tracks)
        create_track_statistic(activity, track)

    return 'Successfully synced data from Garmin Connect'


def get_api():
    api = Garmin(
        settings.ENV('GARMIN_USER'),
        settings.ENV('GARMIN_PASS')
    )
    return api


def create_track(trip: Trip, activity: Dict, tracks: List) -> Track:
    activity_id = str(activity["activityId"])

    time = activity.get('startTimeGMT') + ' +0000'
    time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S %z')

    # if activity id is in the list of tracks, skip it
    if activity_id in list(tracks):
        return

    track = Track.objects.create(
        title=activity_id,
        date=time,
        activity_type='cycling',
        trip=trip
    )

    return track


def create_track_statistic(activity: Dict, track: Track):
    '''{
        'activityId': 9164520465,
        'activityName': 'Vilnius Road Cycling',
        'startTimeLocal': '2022-07-08 17:38:31',
        'startTimeGMT': '2022-07-08 14:38:31',
        'activityType': {
            'typeId': 10,
            'typeKey': 'road_biking',
        },
        'distance': 12652.849609375, m / 1000 = km
        'movingDuration': 1918.14599609375, sec
        'elevationGain': 112.0,
        'elevationLoss': 112.0,
        'averageSpeed': 6.586999893188477,  (m/s) * 3.6 = km/h
        'maxSpeed': 13.222000122070314, (m/s) * 3.6 = km/h
        'startLatitude': 54.644642416387796,
        'startLongitude': 25.181482387706637,
        'calories': 438.0,
        'averageHR': None,
        'maxHR': None,
        'beginTimestamp': 1657291111000,
        'minElevation': 97.80000305175781,
        'maxElevation': 176.0,
        'locationName': 'Vilnius',
        'lapCount': 3,
        'endLatitude': 54.698334792628884,
        'endLongitude': 25.223554093390703,
    } '''

    stats = {
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

    Statistic.objects.create(track=track, **stats)


def filter_non_cycling_activities(activities: List[Dict]) -> List[Dict]:
    _activities = []

    # skip not cycling activities
    for activity in activities:
        activity_type = activity['activityType']['typeKey']
        if not any(x in activity_type for x in ('biking', 'cycling')):
            continue

        _activities.append(activity)

    return _activities


def get_activities(api):
    return api.get_activities(0, 1)  # 0=start, 1=limit


def save_tcx_file(api, activities):
    for activity in activities:
        activity_id = activity["activityId"]
        output_file = os.path.join(settings.MEDIA_ROOT, 'tracks', f'{activity_id}.tcx')

        if os.path.exists(output_file):
            continue

        tcx_data = api.download_activity(activity_id, dl_fmt=api.ActivityDownloadFormat.TCX)

        with open(output_file, "wb") as fb:
            fb.write(tcx_data)
