import os
from typing import List

from django.conf import settings
from tcxreader.tcxreader import TCXReader
from tcxreader.tcx_exercise import TCXExercise
from ..models import Track, Trip, Statistic
from ..utils.common import get_trip


class TracksService:
    def __init__(self, trip: Trip = None):
        self.trip = get_trip() if not trip else trip

    def save_data(self) -> str:
        if not self.trip:
            return 'No trip found'

        files = self.get_files()
        if not files:
            return f'No tcx files in {settings.MEDIA_ROOT}/tracks'

        ids = self.track_list_for_update(files)
        if not ids:
            return 'All tracks are updated'

        self.save_track_and_statistic(ids)

        return 'Successfully synced data from tcx files'

    def get_files(self) -> List[str]:
        directory = os.path.join(settings.MEDIA_ROOT, 'tracks')
        lst = os.listdir(directory)

        files = []
        for file in lst:
            # only .tcx files
            if not file.endswith('.tcx'):
                continue

            # remove extension
            files.append(file[:-4])

        return files

    def track_list_for_update(self, files: List[str]) -> List[Track]:
        # get all tracks for current trip
        tracks = \
            Track.objects \
            .filter(trip=self.trip) \
            .values_list('title', flat=True)

        # find tracks withount statistic
        ids = list(set(files) - set(tracks))

        return list(ids)

    def get_data_from_tcx_file(self, file) -> TCXExercise:
        file = os.path.join(settings.MEDIA_ROOT, 'tracks', f'{file}.tcx')

        if not os.path.exists(file):
            return

        reader = TCXReader()
        data = reader.read(file)

        return data

    def save_track_and_statistic(self, ids: List):
        for id in ids:
            activity = self.get_data_from_tcx_file(id)

            # create track
            track = Track.objects.create(
                title=id,
                date=activity.start_time,
                activity_type=activity.activity_type,
                trip=self.trip
            )

            # create track statistics
            stats = {
                'total_km': activity.distance / 1000,
                'total_time_seconds': activity.duration,
                'avg_speed': activity.avg_speed,
                'max_speed': activity.max_speed,
                'calories': activity.calories,
                'avg_cadence': activity.cadence_avg,
                'avg_heart': activity.hr_avg,
                'max_heart': activity.hr_max,
                'min_altitude': activity.altitude_min,
                'max_altitude': activity.altitude_max,
                'ascent': activity.ascent,
                'descent': activity.descent,
            }

            Statistic.objects.create(track=track, **stats)
