from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from ...utils.garmin_service import GarminService
from ...utils.points_service import PointsService
from ...utils.tracks_service import TracksService


class Command(BaseCommand):
    help = "Get bike activities from Garmin"

    def handle(self, *args, **options):
        try:
            # get data from garmin connect
            GarminService().get_data()

            # write tracks and statistic to database
            TracksService().save_data()

            # get data from tcx files
            PointsService().update_points()
        except Exception as e:
            raise CommandError(f"Can't sync with Garmin - {e}")

        self.stdout.write(
            self.style.SUCCESS(f"{datetime.now()}: successfully get Garmin activities")
        )
