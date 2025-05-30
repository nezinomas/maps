from datetime import datetime
from pathlib import Path

from django.contrib.gis.geos import LineString
from lxml import etree


def get_track_path(file_path: Path) -> LineString:
    namespaces = {
        "ns": "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2",
        "ns3": "http://www.garmin.com/xmlschemas/ActivityExtension/v2",
    }

    coordinates = []
    context = etree.iterparse(
        file_path,
        tag="{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Trackpoint",
    )
    _lon = "ns:LongitudeDegrees/text()"
    _lat = "ns:LatitudeDegrees/text()"
    for _, elem in context:
        pos = elem.xpath("ns:Position", namespaces=namespaces)
        if (
            pos
            and (lon := pos[0].xpath(_lon, namespaces=namespaces))
            and (lat := pos[0].xpath(_lat, namespaces=namespaces))
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

    # Define the namespace for TCX
    namespaces = {"ns": "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"}

    # Extract datetime from the Activity Id
    activity = root.find(".//ns:Activity", namespaces)
    activity_id = activity.find("ns:Id", namespaces)
    if activity_id is None:
        return datetime.now()

    return datetime.fromisoformat(activity_id.text.replace("Z", "+00:00"))
