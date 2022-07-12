from .utils import garmin, points_service
from .utils.wp_comments_qty import push_all_comment_qty as qty


def my_scheduled_job():
    # get data from garmin connect
    # activity summary and activity tcx files
    garmin.get_data()

    # get data from tcx files
    points_service.PointsService().update_points()


def push_comment_qty():
    qty()
