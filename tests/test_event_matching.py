"""Regression tests for event lookup without a UID."""

from datetime import datetime, timedelta

import pytest
from khal.cli import main_khal
from orgparse.date import OrgDate

from khalorg.commands import new
from khalorg.helpers import get_default_khalorg_format
from khalorg.khal.calendar import Calendar
from khalorg.khal.checker import EventChecker
from khalorg.khal.helpers import remove_tzinfo
from khalorg.org.agenda_items import OrgAgendaItem
from tests.helpers import khal_runner


@pytest.fixture
def runner(tmpdir, monkeypatch):
    """Run calendar commands against temporary calendar files."""
    calendar_runner = khal_runner(tmpdir, monkeypatch)()

    def new_item(_, args):
        result = calendar_runner.invoke(main_khal, ["new", *args])
        assert result.exit_code == 0, result.output
        return result.output

    monkeypatch.setattr(Calendar, "new_item", new_item)
    return calendar_runner


@pytest.fixture
def meeting():
    """Return a meeting scheduled for tomorrow morning."""
    start = (datetime.now() + timedelta(days=1)).replace(
        hour=10, minute=0, second=0, microsecond=0
    )
    return OrgAgendaItem(
        title="Meeting",
        timestamps=[OrgDate(start, start + timedelta(hours=1))],
        properties={},
        description="Original meeting",
    )


@pytest.mark.parametrize("start_offset", [-30, 0, 30])
@pytest.mark.parametrize("with_timezone", [False, True])
def test_lookup_matches_start_time(
    runner, meeting, start_offset, with_timezone
):
    """Equal titles and end times do not identify different starts."""
    new("one", org=format(meeting, get_default_khalorg_format()))
    calendar = Calendar("one")
    start = meeting.first_timestamp.start + timedelta(minutes=start_offset)
    end = meeting.first_timestamp.end
    if with_timezone:
        timezone = calendar.config["locale"]["default_timezone"]
        start = timezone.localize(start)
        end = timezone.localize(end)

    matches = calendar.get_events_no_uid(meeting.title, start, end)

    assert len(matches) == (1 if start_offset == 0 else 0)
    if matches:
        assert remove_tzinfo(matches[0].start) == remove_tzinfo(start)


@pytest.mark.parametrize("all_day", [False, True])
def test_lookup_retains_default_end(runner, meeting, all_day):
    """An omitted end still uses khal's timed or all-day default."""
    if all_day:
        meeting.timestamps = [OrgDate(meeting.first_timestamp.start.date())]
    new("one", org=format(meeting, get_default_khalorg_format()))

    matches = Calendar("one").get_events_no_uid(
        meeting.title, meeting.first_timestamp.start, None
    )

    assert len(matches) == 1
    assert remove_tzinfo(matches[0].start) == meeting.first_timestamp.start


@pytest.mark.parametrize("all_day", [False, True])
def test_new_allows_different_starts(runner, meeting, caplog, all_day):
    """Creating a second event preserves each event's UID and description."""
    start = meeting.first_timestamp.start
    end = meeting.first_timestamp.end
    if all_day:
        start = start.date()
        end = start + timedelta(days=2)
        meeting.timestamps = [OrgDate(start, end)]
        second_start = start + timedelta(days=1)
    else:
        second_start = start + timedelta(minutes=30)
    second = OrgAgendaItem(
        title=meeting.title,
        timestamps=[OrgDate(second_start, end)],
        properties={},
        description="Second meeting",
    )
    new("one", org=format(meeting, get_default_khalorg_format()))
    new("one", org=format(second, get_default_khalorg_format()))

    calendar = Calendar("one")
    original_matches = calendar.get_events_no_uid(meeting.title, start, end)
    second_matches = calendar.get_events_no_uid(second.title, second_start, end)

    assert EventChecker.MESSAGE_DUPLICATE not in caplog.text
    assert len(original_matches) == len(second_matches) == 1
    assert original_matches[0].uid != second_matches[0].uid
    assert original_matches[0].description == meeting.description
    assert second_matches[0].description == second.description
