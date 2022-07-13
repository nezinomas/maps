from .utils.garmin_service import GarminService
from .utils.points_service import PointsService
from .utils.wp_comments_qty import push_all_comment_qty as qty


def get_data_from_garminconnect():
    # get data from garmin connect
    GarminService().get_data()

    # get data from tcx files
    PointsService().update_points()


def push_comment_qty():
    qty()
