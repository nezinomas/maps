import logging
from datetime import date, datetime, timezone
from operator import contains

from django.conf import settings
from garminconnect import (Garmin, GarminConnectAuthenticationError,
                           GarminConnectConnectionError,
                           GarminConnectTooManyRequestsError)

from ..models import Track, Trip

# Configure debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def get_data():
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

    try:
        trip = \
            Trip.objects \
            .filter(end_date__gte=date.today()) \
            .order_by('id') \
            .latest('id')
    except Trip.DoesNotExist:
        return('No trip found')

    tracks = \
        Track.objects \
        .filter(trip=trip) \
        .values_list('title', flat=True)

    id_list = []
    for activity in activities:
        activity_id = activity["activityId"]

        time = activity.get('startTimeGMT') + ' +0000'
        time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S %z')

        # if activity id is in the list of tracks, skip it
        if str(activity_id) in list(tracks):
            continue

        # skip not cycling activities
        activity_type = activity['activityType']['typeKey']
        if not any(x in activity_type for x in ('biking', 'cycling')):
            continue

        Track.objects.create(
            title=activity_id,
            date=time,
            activity_type='cycling',
            trip=trip
        )

        id_list.append(activity_id)

    # download and save activities
    for id in id_list:
        save_tcx_file(api, id)

def get_api():
    api = Garmin(
        settings.ENV('GARMIN_USER'),
        settings.ENV('GARMIN_PASS')
    )
    return api


def get_activities(api):
    return api.get_activities(0, 1)  # 0=start, 1=limit

#     try:
#         # API

#         ## Initialize Garmin api with your credentials
#         api = Garmin(
#             settings.ENV('GARMIN_USER'),
#             settings.ENV('GARMIN_PASS')
#         )

#         ## Login to Garmin Connect portal
#         api.login()

#         activities = api.get_activities(0,1) # 0=start, 1=limit

#         return activities

#         '''
#         {
#             'activityId': 9164520465,
#             'activityName': 'Vilnius Road Cycling',
#             'startTimeLocal': '2022-07-08 17:38:31',
#             'startTimeGMT': '2022-07-08 14:38:31',
#             'activityType': {
#                 'typeId': 10,
#                 'typeKey': 'road_biking',
#             },
#             'distance': 12652.849609375, m / 1000 = km
#             'movingDuration': 1918.14599609375, sec
#             'elevationGain': 112.0,
#             'elevationLoss': 112.0,
#             'averageSpeed': 6.586999893188477,  (m/s) * 3.6 = km/h
#             'maxSpeed': 13.222000122070314, (m/s) * 3.6 = km/h
#             'startLatitude': 54.644642416387796,
#             'startLongitude': 25.181482387706637,
#             'calories': 438.0,
#             'averageHR': None,
#             'maxHR': None,
#             'beginTimestamp': 1657291111000,
#             'minElevation': 97.80000305175781,
#             'maxElevation': 176.0,
#             'locationName': 'Vilnius',
#             'lapCount': 3,
#             'endLatitude': 54.698334792628884,
#             'endLongitude': 25.223554093390703,
#         }

#         '''
#         # ## Download an Activity
#         for activity in activities:
#             print(f'\n\nactivity: {activity}')
#             activity_id = activity["activityId"]


#             distance = float(activity.get("distance")) / 1000
#             time = float(activity.get("movingDuration"))

#             avg_speed = float(activity.get("averageSpeed")) * 3.6
#             max_speed = float(activity.get("maxSpeed")) * 3.6
#             ascent = float(activity.get("elevationGain"))
#             descent = float(activity.get("elevationLoss"))
#             calories = int(activity.get("calories"))
#             max_altitude = float(activity.get("maxElevation"))
#             min_alititude = float(activity.get("minElevation"))

#             start_longitude = float(activity.get("startLongitude"))
#             start_latitude = float(activity.get("startLatitude"))
#             end_longitude = float(activity.get("endLongitude"))
#             end_latitude = float(activity.get("endLatitude"))

#             avg_heart = None
#             try:
#                 avg_heart = float(activity.get("averageHR"))
#             except (TypeError, ValueError):
#                 pass

#             max_heart = None
#             try:
#                 max_heart = float(activity.get("maxHR"))
#             except (TypeError, ValueError):
#                 pass

#             avg_cadence = None
#             try:
#                 avg_cadence = float(activity.get("averageBikingCadenceInRevPerMinute"))
#             except (TypeError, ValueError):
#                 pass

#             print(f'total_time_seconds: {time}')
#             print(f'total_km: {distance}')
#             print(f'avg_speed: {avg_speed}')
#             print(f'max_speed: {max_speed}')
#             print(f'ascent: {ascent}')
#             print(f'descent: {descent}')
#             print(f'min_altitude: {min_alititude}')
#             print(f'max_altitude: {max_altitude}')
#             print(f'calories: {calories}')
#             print(f'avg_heart: {avg_heart}')
#             print(f'max_heart: {max_heart}')
#             print(f'avg_cadence: {avg_cadence}')

#     except (
#             GarminConnectConnectionError,
#             GarminConnectAuthenticationError,
#             GarminConnectTooManyRequestsError,
#         ) as err:
#         logger.error("Error occurred during Garmin Connect communication: %s", err)


def save_tcx_file(api, activity_id):
    # tcx_data = api.download_activity(activity_id, dl_fmt=api.ActivityDownloadFormat.TCX)
    # output_file = f"./{str(activity_id)}.tcx"
    # with open(output_file, "wb") as fb:
    #     fb.write(tcx_data)
    # print(f'\n\n\nDONE: {output_file}\n\n')
    pass

