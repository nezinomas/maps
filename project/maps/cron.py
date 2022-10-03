from .utils.garmin_service import GarminService
from .utils.points_service import PointsService
from .utils.tracks_service import TracksService
from .utils.wp_comments_qty import push_comments_qty_for_all_trips as qty


def get_data_from_garminconnect():
    # get data from garmin connect
    GarminService().get_data()

    # write tracks and statistic to database
    TracksService().save_data()

    # get data from tcx files
    PointsService().update_points()


def push_comment_qty():
    qty()
