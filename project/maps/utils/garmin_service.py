import io
import json
import logging
import os
import shutil
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Dict, List

import requests
from django.conf import settings
from garminconnect import (
    Garmin,
    GarminConnectAuthenticationError,
    GarminConnectConnectionError,
    GarminConnectTooManyRequestsError,
)

from ..utils.common import get_trip

logger = logging.getLogger(__name__)

# The token store is shared with the bikes site: one Garmin account, one folder
# (root:garmin 2770), both site users in the 'garmin' group. garminconnect
# writes its token file as 0600, which locks the other site out and sends it
# to a password login (and Garmin's 429s) on every run. Every write from here
# is made group-readable again.
TOKEN_FILE_NAME = "garmin_tokens.json"
SHARED_TOKEN_MODE = 0o660


def token_file(tokenstore: Path) -> Path:
    """The file garminconnect reads and writes for a token store path."""
    if tokenstore.is_dir() or tokenstore.suffix.lower() != ".json":
        return tokenstore / TOKEN_FILE_NAME
    return tokenstore


def share_token_file(path: Path) -> None:
    if path.is_symlink():
        logger.warning("Garmin token file %s is a symlink; mode left alone", path)
        return
    try:
        os.chmod(path, SHARED_TOKEN_MODE)
    except OSError as e:
        logger.warning("Cannot make Garmin token file %s group-readable: %s", path, e)


def keep_tokens_shared(client) -> None:
    """Wrap client.dump, so a login and a token refresh both leave the file shared."""
    library_dump = client.dump

    def dump(path: str) -> None:
        library_dump(path)
        share_token_file(token_file(Path(path).expanduser()))

    client.dump = dump


def warn_if_unreadable(path: Path) -> None:
    """Say why a saved token is not used, instead of a silent password login."""
    if not path.exists() or os.access(path, os.R_OK):
        return
    st = path.stat()
    logger.warning(
        "Garmin token file %s is not readable by this user (owner uid %s, "
        "mode %o): logging in with the password instead. The other site wrote "
        "it owner-only; it must be group-readable (%o).",
        path,
        st.st_uid,
        st.st_mode & 0o777,
        SHARED_TOKEN_MODE,
    )


class GarminApi:
    def __init__(self):
        self._api = self._create_api()

    def __bool__(self):
        return self._api is not None

    def _create_api(self):
        username = settings.ENV["GARMIN_USER"]
        password = settings.ENV["GARMIN_PASS"]
        tokenstore_path = Path(settings.ENV["GARMIN_TOKEN_STORE"]).expanduser()

        # Ensure directory exists
        if not tokenstore_path.parent.exists():
            tokenstore_path.parent.mkdir(parents=True, exist_ok=True)

        warn_if_unreadable(token_file(tokenstore_path))

        try:
            garmin = Garmin(
                email=username,
                password=password,
                is_cn=False,
                return_on_mfa=False,
            )
            keep_tokens_shared(garmin.client)
            # Resumes from the saved token; the password is used only when the
            # token is missing, unreadable or rejected.
            garmin.login(str(tokenstore_path))

            return garmin

        except (
            GarminConnectAuthenticationError,
            GarminConnectTooManyRequestsError,
            FileNotFoundError,
            GarminConnectConnectionError,
            requests.exceptions.HTTPError,
        ) as e:
            logger.warning("Garmin login failed: %s", e)
            return None

    def get_activities(self, start: int, limit: int):
        return self._api.get_activities(start, limit)

    def get_activities_by_date(self, start_date: str, end_date: str):
        if isinstance(start_date, date):
            start_date = start_date.strftime("%Y-%m-%d")

        if isinstance(end_date, date):
            end_date = end_date.strftime("%Y-%m-%d")

        return self._api.get_activities_by_date(start_date, end_date)

    def download_tcx(self, activity_id):
        return self._api.download_activity(
            activity_id, dl_fmt=self._api.ActivityDownloadFormat.TCX
        )

    def download_fit(self, activity_id):
        data = self._api.download_activity(
            activity_id, dl_fmt=self._api.ActivityDownloadFormat.ORIGINAL
        )

        # Check if data is a ZIP archive
        if data.startswith(b"PK\x03\x04"):  # ZIP magic number
            with io.BytesIO(data) as zip_buffer:
                with zipfile.ZipFile(zip_buffer) as z:
                    if fit_files := [
                        f for f in z.namelist() if f.lower().endswith(".fit")
                    ]:
                        # Extract first .FIT file
                        data = z.read(fit_files[0])

                    else:
                        return None
        return data


# Custom exception
class GarminServiceError(Exception):
    pass


class GarminService:
    def __init__(
        self, trip=None, start_date=None, end_date=None, activity_types=None, api=None
    ):
        self.trip = trip or get_trip()
        self.start_date = start_date
        self.end_date = end_date
        self.activity_types = activity_types or ["biking", "cycling"]

        self.api = api or GarminApi()

    def get_data(self) -> str:
        if not self.trip:
            return "No trip found"

        if not self.api:
            return "Error occurred during Garmin Connect communication"

        try:
            activities = self._fetch_activities()
            filtered_activities = self._filter_activities(activities)

            if not filtered_activities:
                return "Nothing to sync"

            self._save_activities(filtered_activities)

            return "Successfully synced data from Garmin Connect"
        except GarminServiceError as e:
            return f"Error: {e}"

    def _fetch_activities(self) -> List[Dict]:
        try:
            if self.start_date and self.end_date:
                return self.api.get_activities_by_date(self.start_date, self.end_date)
            return self.api.get_activities(0, 15)
        except Exception as e:
            raise GarminServiceError(f"Failed to fetch activities: {str(e)}") from e

    def _filter_activities(self, activities: List[Dict]) -> List[Dict]:
        def is_valid_activity(activity: Dict) -> bool:
            # Filter by activity type
            activity_type = activity["activityType"]["typeKey"].lower()
            if all(x not in activity_type for x in self.activity_types):
                return False

            # Skip date filter if start_date and end_date are provided
            if self.start_date and self.end_date:
                return True

            # Filter by trip date range
            try:
                time = datetime.strptime(
                    activity.get("startTimeGMT"), "%Y-%m-%d %H:%M:%S"
                )
                time = time.replace(tzinfo=timezone.utc)
                trip_start = datetime.combine(
                    self.trip.start_date, datetime.min.time(), tzinfo=timezone.utc
                )
                trip_end = datetime.combine(
                    self.trip.end_date, datetime.min.time(), tzinfo=timezone.utc
                )
                return trip_start <= time <= trip_end
            except (ValueError, TypeError):
                return False

        return [activity for activity in activities if is_valid_activity(activity)]

    def _save_activities(self, activities: List[Dict]) -> None:
        file_type = "fit"
        try:
            tracks_folder = Path(settings.MEDIA_ROOT) / "tracks" / str(self.trip.pk)

            if not tracks_folder.exists():
                tracks_folder.mkdir(parents=True, exist_ok=True)

            for activity in activities:
                activity_id = activity["activityId"]

                activity_summary_file = tracks_folder / str(activity_id)
                if activity_summary_file.exists():
                    continue

                activity_file = self.api.download_fit(activity_id)
                with open(f"{activity_summary_file}.{file_type}", "wb") as f:
                    f.write(activity_file)

                with open(activity_summary_file, "w") as f:
                    json.dump(activity, f)

        except Exception as e:
            raise GarminServiceError(f"Failed to save activities: {e}") from e
