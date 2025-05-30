from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from ...utils.garmin_service import GarminService


class Command(BaseCommand):
    help = "Get bike activities from Garmin"

    def handle(self, *args, **options):
        try:
            # get data from garmin connect
            GarminService().get_data()
        except Exception as e:
            raise CommandError(f"It is not possible to sync data with Garmin - {e}") from e

        self.stdout.write(
            self.style.SUCCESS(
                f"{datetime.now()}: Garmin activities have been successfully synced."
            )
        )
