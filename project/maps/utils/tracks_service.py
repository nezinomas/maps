from pathlib import Path
from typing import Dict, List, Set

from django.conf import settings

from ..models import Statistic, Track, Trip
from ..utils.common import get_trip
from . import parse_activity_file, parse_fit_file

class TracksServiceData:
    def __init__(self, trip: Trip = None) -> List[str]:
        self.trip = trip or get_trip()
        self.tracks_db = self.get_tracks()
        self.tracks_disk = self.get_files()

    def get_tracks(self) -> Dict:
        return self.trip.tracks.values("pk", "title", "date", "path")

    def get_files(self) -> Set[str]:
        directory = Path(settings.MEDIA_ROOT) / "tracks" / str(self.trip.pk)

        if not directory.exists():
            return set()

        return {file.stem for file in directory.glob("*.fit")}


class TracksService:
    def __init__(self, data: TracksServiceData):
        self.trip = data.trip

        try:
            self.tracks_db = {track["title"] for track in data.tracks_db}
        except AttributeError:
            self.tracks_db = set()

        try:
            self.tracks_title_pk_map = {
                track["title"]: track["pk"] for track in data.tracks_db
            }
        except AttributeError:
            self.tracks_title_pk_map = {}

        self.tracks_disk = data.tracks_disk

    def new_tracks(self) -> Set[str]:
        return self.tracks_disk - self.tracks_db

    def _save_tracks(self, tracks):
        Track.objects.bulk_create(
            tracks,
            update_conflicts=True,
            update_fields=["date", "path"],
            unique_fields=["pk"],
        )

    def _create_tracks(self, track_list):
        tracks = []
        file_type = "fit"

        for track in track_list:
            track_file = (
                Path(settings.MEDIA_ROOT)
                / "tracks"
                / str(self.trip.pk)
                / f"{track}.{file_type}"
            )

            path = parse_fit_file.get_track_path(track_file)
            date = parse_fit_file.get_track_date(track_file)

            obj = Track(
                title=track,
                date=date,
                activity_type="cycling",
                trip=self.trip,
                path=path,
            )

            # If the track already exists in the database
            # set its primary key for update
            if track in self.tracks_title_pk_map:
                obj.pk = self.tracks_title_pk_map[track]

            tracks.append(obj)
        return tracks

    def _save_statistic(self, tracks):
        objects = []
        statistic_model_fields = []
        for track in tracks:
            activity_file = (
                Path(settings.MEDIA_ROOT) / "tracks" / str(self.trip.pk) / track.title
            )

            stats = parse_activity_file.get_statistic(activity_file)
            if not stats:
                continue

            obj = Statistic(track=track, **stats)
            objects.append(obj)

            # if statistic_model_fields is empty,
            # use the keys from the first stats dictionary
            if not statistic_model_fields:
                statistic_model_fields = list(stats.keys())

        Statistic.objects.bulk_create(
            objects,
            update_conflicts=True,
            update_fields=statistic_model_fields,
            unique_fields=["track"],
        )

    def _write_tracks(self, tracks):
        try:
            self._save_tracks(tracks)
        except Exception as e:
            return f"Error occurred during saving tracks: {e}"
        try:
            self._save_statistic(tracks)
        except Exception as e:
            return f"Error occurred during saving statistic: {e}"

        return "Successfully created or updated tracks and statistics"

    def create(self) -> tuple[str, int]:
        """
        Returns a tuple with a message and the number of new tracks created.
        """
        new_tracks = self.new_tracks()
        tracks = self._create_tracks(new_tracks), len(new_tracks)

        return self._write_tracks(tracks)

    def create_or_update(self) -> tuple[str, int]:
        """
        Returns a tuple with a message and the number of new tracks created.
        """
        tracks = self._create_tracks(self.tracks_db | self.tracks_disk)
        return self._write_tracks(tracks)
