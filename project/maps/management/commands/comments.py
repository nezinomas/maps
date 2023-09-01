from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from ...utils.wp_comments_qty import push_comments_qty_for_all_trips as qty


class Command(BaseCommand):
    help = "Get bike activities from Garmin"

    def handle(self, *args, **options):
        try:
            qty()
        except Exception as e:
            raise CommandError(f"Can't sync with Wordpress - {e}")

        self.stdout.write(
            self.style.SUCCESS(f"{datetime.now()}: successfully pushed comments")
        )
