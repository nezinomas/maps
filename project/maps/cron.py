from .utils import update_track_points as importer


def my_scheduled_job():
    importer.update_track_points()
