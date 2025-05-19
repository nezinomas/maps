import os
from datetime import timezone
from typing import List

from django.conf import settings
from django.template.loader import render_to_string
from tcxreader.tcxreader import TCXReader

from ..models import Point, Track, Trip
from .common import get_trip


class PointsService():
    def __init__(self, trip: Trip = None):
        self.trip = trip or get_trip()

    def update_points(self) -> List[str]:
        if not self.trip:
            return ['No active trip']

        # get tracks with no points
        tracks = self.get_tracks_with_no_points()
        if not tracks:
            return ['No track.points needs to insert']

        messages = []
        try:
            messages += self.points_to_db(tracks)
        except Exception as e:
            messages += e

        messages += self.regenerate_points_file()

        return messages

    def update_all_points(self) -> List[str]:
        # delete all points
        Point.objects.filter(track__trip=self.trip).delete()

        return self.update_points()

    def regenerate_points_file(self) -> List[str]:
        if not self.trip:
            return ['No active trip']

        # get trip all tracks
        tracks_qs = \
                Track.objects \
                .select_related('stats') \
                .filter(trip=self.trip)

        if not tracks_qs:
            return [f'No tracks for trip {self.trip.title}']

        tracks = []
        for track in tracks_qs:
            if points := list(map(list, track.points.values_list('latitude', 'longitude'))):
                tracks.append({
                    'track': track,
                    'points': points,
                    'last_point' : points[-1],
                })

        try:
            msg = self.points_to_js(tracks)
        except Exception as e:
            msg = [e]

        return msg

    def points_to_db(self, tracks: List[Track]) -> List[str]:
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

        return ['Points inserted']

    def points_to_js(self, tracks: List[Track]) -> List[str]:
        file = os.path.join(
            settings.MEDIA_ROOT,
            'points',
            f'{self.trip.pk}-points.js'
        )

        last = \
            Point.objects \
            .filter(track__trip=self.trip) \
            .order_by('-track__date', '-datetime') \
            .values_list('latitude', 'longitude')[:1]

        last_point = {
            'latitude': last[0][0] if last else 0,
            'longitude': last[0][1] if last else 0
        }

        with open(file, 'w') as js_file:
            context = {
                'tracks': tracks,
                'last_point': last_point,
            }
            content = render_to_string('maps/points.html', context)
            js_file.write(content)

        return ['Points written to js file']

    def get_tracks_with_no_points(self) -> List[Track]:
        tracks = \
            Track.objects \
            .filter(trip=self.trip) \
            .values_list('pk', flat=True)

        points = \
            Point.objects \
            .filter(track__trip=self.trip) \
            .values_list('track__pk', flat=True)

        ids = list(set(tracks) - set(points))

        return Track.objects.filter(pk__in=ids)

    def get_data_from_tcx_file(self, file) -> TCXReader:
        file = os.path.join(
            settings.MEDIA_ROOT,
            'tracks',
            str(self.trip.pk),
            f'{file}.tcx'
        )

        if not os.path.exists(file):
            return None

        return TCXReader().read(file)
