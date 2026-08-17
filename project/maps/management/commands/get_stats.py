from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from ...utils.common import get_trip
from ...utils.tracks_service import TracksService, TracksServiceData
from ...utils.views_map import set_cache


class Command(BaseCommand):
    help = "Process Garmin activities, save tracks and statistics to the database"

    def handle(self, *args, **options):
        trip = get_trip()
        if not trip:
            self.stdout.write(self.style.SUCCESS(f"{datetime.now()}: No active trip."))
            return

        obj = None
        track_qty = 0

        try:
            data = TracksServiceData()
            obj = TracksService(data)
            _, track_qty = obj.create()
        except Exception as e:
            raise CommandError(f"Can't write data to DB - {e}") from e

        # set cache after writing to DB
        if track_qty > 0:
            try:
                set_cache(obj.trip)
            except Exception as e:
                raise CommandError(f"Can't set cache - {e}") from e

        dt = datetime.now()
        if track_qty > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"{dt}: {track_qty} tracks have been successfully synced."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"{dt}: No new tracks to sync for {obj.trip.title}.")
            )
