from .utils import update_track_points as importer
from .utils.wp_comments_qty import push_all_comment_qty as qty


def my_scheduled_job():
    importer.update_all_trips()


def push_comment_qty():
    qty()
