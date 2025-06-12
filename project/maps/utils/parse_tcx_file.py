from datetime import datetime
from pathlib import Path

from django.contrib.gis.geos import LineString
from lxml import etree

NAMESPACES = {
    "ns": "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2",
    "ns3": "http://www.garmin.com/xmlschemas/ActivityExtension/v2",
}

TRACKPOINT_TAG = (
    "{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Trackpoint"
)

LON = "ns:LongitudeDegrees/text()"
LAT = "ns:LatitudeDegrees/text()"


def get_track_path(file_path: Path) -> LineString:
    coordinates = []
    context = etree.iterparse(
        file_path,
        tag=TRACKPOINT_TAG,
    )
    for _, elem in context:
        pos = elem.xpath("ns:Position", namespaces=NAMESPACES)
        if (
            pos
            and (lon := pos[0].xpath(LON, namespaces=NAMESPACES))
            and (lat := pos[0].xpath(LAT, namespaces=NAMESPACES))
        ):
            coordinates.append((round(float(lon[0]), 5), round(float(lat[0]), 5)))
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]  # Clear parent to reduce memory

    if not coordinates or len(coordinates) < 2:
        raise "No valid coordinates found in TCX file"

    return LineString(coordinates, srid=4326)


def get_track_date(file_path: Path) -> datetime:
    tree = etree.parse(file_path)
    root = tree.getroot()

    # Extract datetime from the Activity Id
    activity = root.find(".//ns:Activity", NAMESPACES)
    activity_id = activity.find("ns:Id", NAMESPACES)
    if activity_id is None:
        return datetime.now()

    return datetime.fromisoformat(activity_id.text.replace("Z", "+00:00"))
