import os
from datetime import timezone

from django.conf import settings
from django.template.loader import render_to_string
from tcxreader.tcxreader import TCXReader

from ..models import Point, Track, Trip
from .common import get_trip

'''
{TCXExercise}
    activity_type = {str} 'Biking'
    ascent = {float} 1404.400026500225
    avg_speed = {float} 24.285282782608693
    cadence_avg = {NoneType} None
    cadence_max = {NoneType} None
    calories = {int} 2010
    descent = {float} 1422.000026166439
    distance = {float} 116366.98
    duration = {float} 17250.0
    end_time = {datetime} 2015-02-19 14:18:59+00:00
    hr_avg = {float} 140.59545804464972
    hr_max = {int} 200
    hr_min = {int} 94
    altitude_max = {float}
    altitude_min = {float}
    altitude_avg = {float}
    max_speed = {float} 18.95800018310547
    start_time = {datetime} 2015-02-19 09:31:29+00:00
    trackpoints = {list: 7799} [TCXTrackPoint]
'''

class PointsService():
    def __init__(self, trip: Trip = None):
        self._trip = get_trip() if not trip else trip

    def update_points(self):
        if not self._trip:
            return('No active trip')

        # get tracks with no points
        tracks = self.get_tracks_with_no_points()
        if not tracks:
            return('No track.points needs to insert')

        self.points_to_db(tracks)
        self.points_to_js(tracks)

        return('Points inserted')

    def update_all_points(self):
        # delete all points
        Point.objects.filter(track__trip=self._trip).delete()

        return self.update_points()

    def points_to_db(self, tracks):
        # get points from tcx files and write them to db
        for track in tracks:
            points = self.get_data_from_tcx_file(track.title).trackpoints

            if not points:
                continue

            objs = [
                Point(
                    latitude=point.latitude,
                    longitude=point.longitude,
                    altitude=point.elevation,
                    distance_meters=point.distance,
                    cadence=point.cadence,
                    heart_rate=point.hr_value,
                    datetime=point.time.astimezone(timezone.utc),
                    track=track
                )
                for point in points
            ]

            Point.objects.bulk_create(objs)

    def points_to_js(self, tracks):
        file = os.path.join(settings.MEDIA_ROOT, 'points', f'{self._trip.pk}-points.js')

        with open(file, 'w') as js_file:
            content = render_to_string('maps/generate_js.html', {'tracks': tracks})
            js_file.write(content)

    def get_tracks_with_no_points(self):
        tracks = \
            Track.objects \
            .filter(trip=self._trip) \
            .values_list('pk', flat=True)

        points = \
            Point.objects \
            .filter(track__trip=self._trip) \
            .values_list('track__pk', flat=True)

        ids = list(set(tracks) - set(points))

        return Track.objects.filter(pk__in=ids)

    def get_data_from_tcx_file(self, file):
        file = os.path.join(settings.MEDIA_ROOT, 'tracks', f'{file}.tcx')

        if not os.path.exists(file):
            return

        reader = TCXReader()
        data = reader.read(file)

        return data
