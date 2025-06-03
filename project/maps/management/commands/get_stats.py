from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from ...utils.tracks_service import TracksService, TracksServiceData


class Command(BaseCommand):
    help = "Get bike activities from Garmin"

    def handle(self, *args, **options):
        try:
            # get data from garmin connect
            data = TracksServiceData()
            service = TracksService(data)
            service.create()
        except Exception as e:
            raise CommandError(f"Can't write data to DB - {e}") from e

        self.stdout.write(
            self.style.SUCCESS(f"{datetime.now()}: Data has been writed to DB.")
        )
