import pytest
from datetime import datetime, timezone
from ..utils.parse_tcx_file import get_track_path, get_track_date


@pytest.fixture(name="tcx_file")
def fixture_tcx_file(tmp_path):
    tcx = '<?xml version="1.0" encoding="UTF-8"?>\n'
    tcx += "<TrainingCenterDatabase\n"
    tcx += 'xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd"\n'
    tcx += 'xmlns:ns5="http://www.garmin.com/xmlschemas/ActivityGoals/v1"\n'
    tcx += 'xmlns:ns3="http://www.garmin.com/xmlschemas/ActivityExtension/v2"\n'
    tcx += 'xmlns:ns2="http://www.garmin.com/xmlschemas/UserProfile/v2"\n'
    tcx += 'xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"\n'
    tcx += 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ns4="http://www.garmin.com/xmlschemas/ProfileExtension/v1">\n'
    tcx += "<Activities>\n"
    tcx += '<Activity Sport="Biking">\n'
    tcx += "<Id>2025-05-26T04:28:38.000Z</Id>\n"
    tcx += '<Lap StartTime="2025-05-26T04:28:38.000Z">\n'
    tcx += "<TotalTimeSeconds>828.751</TotalTimeSeconds>\n"
    tcx += "<DistanceMeters>5000.0</DistanceMeters>\n"
    tcx += "<MaximumSpeed>9.572999954223633</MaximumSpeed>\n"
    tcx += "<Calories>137</Calories>\n"
    tcx += "<Intensity>Active</Intensity>\n"
    tcx += "<TriggerMethod>Manual</TriggerMethod>\n"
    tcx += "<Track>\n"
    tcx += "<Trackpoint>\n"
    tcx += "<Time>2025-05-26T04:28:38.000Z</Time>\n"
    tcx += "<Position>\n"
    tcx += "<LatitudeDegrees>54.12345678999999</LatitudeDegrees>\n"
    tcx += "<LongitudeDegrees>25.12345678999999</LongitudeDegrees>\n"
    tcx += "</Position>\n"
    tcx += "<AltitudeMeters>162.1999969482422</AltitudeMeters>\n"
    tcx += "<DistanceMeters>0.0</DistanceMeters>\n"
    tcx += "<Extensions>\n"
    tcx += "<ns3:TPX>\n"
    tcx += "<ns3:Speed>0.0</ns3:Speed>\n"
    tcx += "</ns3:TPX>\n"
    tcx += "</Extensions>\n"
    tcx += "</Trackpoint>\n"
    tcx += "<Trackpoint>\n"
    tcx += "<Time>2025-05-26T04:28:38.000Z</Time>\n"
    tcx += "<Position>\n"
    tcx += "<LatitudeDegrees>64.12345678999999</LatitudeDegrees>\n"
    tcx += "<LongitudeDegrees>35.12345678999999</LongitudeDegrees>\n"
    tcx += "</Position>\n"
    tcx += "<AltitudeMeters>162.1999969482422</AltitudeMeters>\n"
    tcx += "<DistanceMeters>0.0</DistanceMeters>\n"
    tcx += "<Extensions>\n"
    tcx += "<ns3:TPX>\n"
    tcx += "<ns3:Speed>0.0</ns3:Speed>\n"
    tcx += "</ns3:TPX>\n"
    tcx += "</Extensions>\n"
    tcx += "</Trackpoint>\n"
    tcx += "</Track>\n"
    tcx += "</Lap>\n"
    tcx += "</Activity>\n"
    tcx += "</Activities>\n"
    tcx += "</TrainingCenterDatabase>\n"

    file = tmp_path / "test_activity.tcx"
    file.write_text(tcx)
    return file


def test_parsetcx_track_path(tcx_file):
    actual = get_track_path(tcx_file)

    assert actual.coords == ((25.12346, 54.12346), (35.12346, 64.12346))


def test_parsetcx_track_date(tcx_file):
    actual = get_track_date(tcx_file)

    assert actual == datetime(2025, 5, 26, 4, 28, 38, tzinfo=timezone.utc)
