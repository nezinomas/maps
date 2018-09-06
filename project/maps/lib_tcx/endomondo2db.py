import re
import requests  # Verifica PROXY

from ...config.secrets import get_secret
from .. import models

from . import endomondo as e

__VERSION__ = "0.4.2"
__APP__ = "Endomondo Export TCX files"

nl = "\n"
CREDENCIALES = "endomondo_data.txt"
sesion = requests.Session()
ERROR_NO_INTERNET = "ERROR"
MAX_WORKOUTS = 15

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


# create the TCX file for the specified workout
def create_tcx_file(workout):
    # directory_name = 'D:/e'
    activity = workout.get_activity()

    name = create_filename(workout)

    trip = models.Trip.objects.get(pk=1)

    track = trip.tracks.filter(title=name)
    if track:
        print('yra toks')
        return

    dt = workout.start_time
    track = models.Track.objects.create(title=name, date=dt, activity_type=activity.sport, trip=trip)

    lap = activity.laps[0]

    stats = ''
    try:
        stats = models.Statistic.objects.create(
            total_km = lap.distance_km,
            total_time_seconds = lap.total_time_seconds,
            max_speed = lap.maximum_speed,
            calories = lap.calories,
            avg_speed = round((lap.distance_meters/lap.total_time_seconds)*(3600/1000),2),
            avg_cadence = lap.avg_cadence,
            avg_heart = lap.avg_heart,
            max_heart = lap.max_heart,
            avg_temperature = 0.0,
            min_altitude = lap.min_altitude,
            max_altitude = lap.max_altitude,
            track = track
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
                latitude = point.latitude,
                longitude = point.longitude,
                altitude = point.altitude_meters,
                distance_meters = point.distance_meters,
                # cadence = point.
                heart_rate = point.heart_rate,
                # temperature = point.
                datetime = point.timestamp,
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


def credenciales():
    txt = [""]
    try:
        with open(CREDENCIALES, 'r') as r:
            txt = r.read()
            txt = txt.split(nl)
            if len(txt) == 2: txt.append('')    # No proxi en fichero TXT
    except:
        txt = [""]
    return txt

def main():
    try:
        print ("Endomondo: export most recent workouts as TCX files")
        cred = credenciales()

        if len(cred) > 1:
            email, password = cred  # cred[0], cred[1]
            # s_proxy = necesita_proxy(proxy)
            # if s_proxy == ERROR_NO_INTERNET:
            #     print ("No Internet Access. Impossible to continue!")
            #     return 0
        else:
            email =  get_secret("ENDOMONDO_USER")
            password = get_secret("ENDOMONDO_PASS")

        # maximum_workouts = input("Maximum number of workouts (press Enter to ignore) ")
        maximum_workouts = MAX_WORKOUTS
        endomondo = e.Endomondo(email, password)

        workouts = endomondo.get_workouts(maximum_workouts)
        print ("Fetched latest", len(workouts), "workouts")
        for workout in workouts:
            create_tcx_file(workout)
        print ("Export done!!")
        return 0

    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)
        return 1
