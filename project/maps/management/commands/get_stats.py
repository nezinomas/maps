from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from ...utils.tracks_service import TracksService, TracksServiceData
from ...utils.views_map import set_cache


class Command(BaseCommand):
    help = "Get bike activities from Garmin"

    def handle(self, *args, **options):
        obj = None
        track_qty = 0

        try:
            data = TracksServiceData()
            obj = TracksService(data)
            _, track_qty = obj.create()
        except Exception as e:
            raise CommandError(f"Can't write data to DB - {e}") from e

        # set cache after writing to DB
        try:
            if track_qty > 0:
                set_cache(obj.trip)
        except Exception as e:
            raise CommandError(f"Can't set cache - {e}") from e

        self.stdout.write(
            self.style.SUCCESS(f"{datetime.now()}: Data has been writed to DB.")
        )
