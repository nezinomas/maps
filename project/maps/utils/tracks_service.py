import os
from typing import List
from django.conf import settings

from ..models import Trip
from ..utils.common import get_trip


class TracksService:
    def __init__(self, trip: Trip = None):
        self.trip = get_trip() if not trip else trip

    def save_data(self) -> str:
        if not self.trip:
            return 'No trip found'

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
