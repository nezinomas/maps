import os
from datetime import timezone

from django.conf import settings
from django.template.loader import render_to_string
from tcxreader.tcxreader import TCXReader

from ..models import Point, Track, Trip
from .common import get_trip


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
