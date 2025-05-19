import shutil
from os import makedirs, path, remove

from django.conf import settings
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Trip


@receiver(post_save, sender=Trip)
def create_points_file_for_new_trip(sender: object, instance: object, *args, **kwargs):
    pk = instance.pk

    template = path.join(settings.SITE_ROOT, "maps", "templates", "maps", "0-points.js")
    file = path.join(settings.MEDIA_ROOT, "points", f"{pk}-points.js")

    if not path.exists(file):
        shutil.copy2(template, file)

    # create tracks/trip.pk folder
    folder = path.join(settings.MEDIA_ROOT, "tracks", str(pk))
    makedirs(folder, exist_ok=True)


@receiver(post_delete, sender=Trip)
def delete_points_file(sender: object, instance: object, *args, **kwargs):
    pk = instance.pk

    file = path.join(settings.MEDIA_ROOT, "points", f"{pk}-points.js")

    if path.exists(file):
        remove(file)
