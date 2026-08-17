import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from mock import patch

from project.maps.management.commands.comments import Command as CommentsCommand
from project.maps.management.commands.get_data import Command as GetDataCommand
from project.maps.management.commands.get_stats import Command as GetStatsCommand


def test_command_help_texts():
    assert CommentsCommand.help != GetDataCommand.help, (
        "comments.py help text should not be a copy-paste of get_data.py"
    )
    assert GetStatsCommand.help != GetDataCommand.help, (
        "get_stats.py help text should not be a copy-paste of get_data.py"
    )


@patch("project.maps.management.commands.get_stats.TracksServiceData")
@patch("project.maps.management.commands.get_stats.TracksService")
@patch("project.maps.utils.common.get_trip", return_value=None)
def test_get_stats_no_active_trip_does_not_crash(
    mck_get_trip, mck_service, mck_data, capsys
):
    # Call the get_stats command when there is no active trip
    call_command("get_stats")

    captured = capsys.readouterr()
    assert "No active trip" in captured.out or "No active trip" in captured.err
