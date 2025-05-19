import json
import os
from datetime import datetime
from typing import Dict, List

from django.conf import settings

from ..models import Statistic, Track, Trip
from ..utils.common import get_trip


class TracksService:
    def __init__(self, trip: Trip = None) -> List[str]:
        self.trip = trip or get_trip()

    def save_data(self) -> str:
        if not self.trip:
            return ['No trip found']

        files = self.get_files()
        if not files:
            return [f'No sts files in {settings.MEDIA_ROOT}/tracks/{self.trip.pk}/']

        ids = self.track_list_for_update(files)
        if not ids:
            return ['All tracks are updated']

        self.save_track_and_statistic(ids)

        return ['Successfully synced data from sts files']

    def get_files(self) -> List[str]:
        directory = os.path.join(
            settings.MEDIA_ROOT,
            'tracks',
            str(self.trip.pk)
        )
        file_list = os.listdir(directory)

        return [file[:-4] for file in file_list if file.endswith('.sts')]

    def track_list_for_update(self, files: List[str]) -> List[Track]:
        # get all tracks for current trip
        tracks = \
            Track.objects \
            .filter(trip=self.trip) \
            .values_list('title', flat=True)

        # find tracks withount statistic
        ids = list(set(files) - set(tracks))

        return list(ids)

    def get_data_from_sts_file(self, file) -> Dict:
        file = os.path.join(
            settings.MEDIA_ROOT,
            'tracks',
            str(self.trip.pk),
            f'{file}.sts'
        )

        if not os.path.exists(file):
            return None

        with open(file, 'r') as f:
            data = json.load(f)

        return data

    def save_track_and_statistic(self, ids: List):
        for id in ids:
            activity = self.get_data_from_sts_file(id)

            # create track
            track = Track.objects.create(
                title=id,
                date=datetime.strptime(activity['start_time'], '%Y-%m-%d %H:%M:%S %z'),
                activity_type='cycling',
                trip=self.trip
            )

            # create track statistics
            del activity['start_time']

            Statistic.objects.create(track=track, **activity)
