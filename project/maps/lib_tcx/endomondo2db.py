import re
import requests  # Verifica PROXY
import json

from ...config.secrets import get_secret
from .. import models

from . import endomondo as e

__VERSION__ = "0.4.2"
__APP__ = "Endomondo Export TCX files"

nl = "\n"
CREDENCIALES = "endomondo_data.txt"
sesion = requests.Session()
ERROR_NO_INTERNET = "ERROR"
MAX_WORKOUTS = 7


# create a somewhat useful filename for the specified workout
def create_filename(workout):
    ret = ''
    if workout.start_time:
        ret = workout.start_time.strftime("%Y%m%d") + "_"
    ret += str(workout.id)
    name = workout.name
    if name:
        name = re.sub(r'[\[\]/\\;,><&*:%=+@!#\(\)\|\?\^]', '', name)
        name = re.sub(r"[' \t]", '_', name)
        ret += "_" + name
    return ret


def create_tcx_file(trip, workout, params):
    activity = workout.get_activity()

    name = create_filename(workout)

    track = trip.tracks.filter(title=name)

    if track:
        return 0

    dt = workout.start_time
    track = models.Track.objects.create(title=name, date=dt, activity_type=activity.sport, trip=trip)

    lap = activity.laps[0]

    stats = ''
    try:
        stats = models.Statistic.objects.create(
            total_km=lap.distance_km,
            total_time_seconds=lap.total_time_seconds,
            max_speed=lap.maximum_speed,
            calories=lap.calories,
            avg_speed=round((lap.distance_meters / lap.total_time_seconds) * (3600 / 1000), 2),
            avg_cadence=lap.avg_cadence,
            avg_heart=lap.avg_heart,
            max_heart=lap.max_heart,
            avg_temperature=0.0,
            min_altitude=lap.min_altitude,
            max_altitude=lap.max_altitude,
            ascent=params['ascent'],
            descent=params['descent'],
            track=track
        )
    except Exception as ex:
        track.delete()

        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)

    trackpoints = activity.trackpoints

    try:
        objs = [
            models.Point(
                latitude=point.latitude,
                longitude=point.longitude,
                altitude=point.altitude_meters,
                distance_meters=point.distance_meters,
                # cadence=point.
                heart_rate=point.heart_rate,
                # temperature=point.
                datetime=point.timestamp,
                track=track
            )
            for point in trackpoints
        ]
        models.Point.objects.bulk_create(objs)
    except Exception as ex:
        track.delete()
        stats.delete()

        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)

    return track.pk


def credenciales():
    txt = [""]
    try:
        with open(CREDENCIALES, 'r') as r:
            txt = r.read()
            txt = txt.split(nl)
            if len(txt) == 2:
                txt.append('')    # No proxi en fichero TXT
    except:
        txt = [""]
    return txt


def main(trip):
    try:
        cred = credenciales()

        if len(cred) > 1:
            email, password = cred  # cred[0], cred[1]
        else:
            email = get_secret("ENDOMONDO_USER")
            password = get_secret("ENDOMONDO_PASS")

        endomondo = e.Endomondo(email, password)

        workouts = endomondo.get_workouts(MAX_WORKOUTS)

        inserted_workouts = []
        for workout in workouts:
            id = workout.properties['id']

            url = 'https://www.endomondo.com/rest/v1/users/{}/workouts/{}'.format(get_secret("ENDOMONDO_USER_ID"), id)

            r = workout.parent.request.get(url)

            data = r.json()
            params = {'ascent': 0.0, 'descent': 0.0 }

            if data['ascent']:
                params['ascent'] = float(data['ascent'])

            if data['descent']:
                params['descent'] = float(data['descent'])

            track_id = create_tcx_file(trip, workout, params)
            if track_id > 0:
                inserted_workouts.append(track_id)



        return inserted_workouts

    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)
