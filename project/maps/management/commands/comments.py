from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from ...utils.wp_comments_qty import push_comments_qty_for_all_trips


class Command(BaseCommand):
    help = "Sync WordPress comment quantities for all trips"

    def handle(self, *args, **options):
        try:
            push_comments_qty_for_all_trips()
        except Exception as e:
            raise CommandError(f"Can't sync with Wordpress - {e}") from e

        self.stdout.write(
            self.style.SUCCESS(f"{datetime.now()}: successfully pushed comments.")
        )
