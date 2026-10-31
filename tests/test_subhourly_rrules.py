"""Regression tests for calendar rules without an org repeater equivalent."""

from datetime import datetime, time, timedelta
from pathlib import Path

import pytest
from icalendar import Calendar as ICalendar
from icalendar import Event
from orgparse.date import OrgDate

from khalorg.commands import list_command
from khalorg.helpers import get_default_khalorg_format
from khalorg.org.agenda_items import OrgAgendaFile, OrgDateAgenda
from khalorg.rrule import (
    rrulestr_is_supported,
    rrulestr_to_org,
)
from tests.test_commands import get_cli_runner, runner  # noqa: F401


@pytest.mark.parametrize("frequency", ["MINUTELY", "SECONDLY"])
def test_subhourly_rules_have_no_org_repeater(frequency):
    """Valid subhourly rules must use the explicit timestamp fallback."""
    rule = f"FREQ={frequency}"

    assert not rrulestr_is_supported(rule)
    assert rrulestr_to_org(rule) is None


@pytest.mark.parametrize(
    ("frequency", "unit"),
    [
        ("YEARLY", "y"),
        ("MONTHLY", "m"),
        ("WEEKLY", "w"),
        ("DAILY", "d"),
        ("HOURLY", "h"),
    ],
)
def test_supported_frequencies_keep_org_repeaters(frequency, unit):
    """Supported recurrence frequencies retain their interval and unit."""
    rule = f"FREQ={frequency};INTERVAL=2"

    assert rrulestr_is_supported(rule)
    assert rrulestr_to_org(rule) == ("+", 2, unit)


@pytest.mark.parametrize("rule", ["FREQ=MINUTELY", "FREQ=SECONDLY;INTERVAL=60"])
def test_subhourly_grouping_keeps_explicit_occurrences(rule):
    """Occurrences with the same unsupported rule must remain explicit."""
    start = datetime(2030, 1, 1, 10)
    timestamps = [
        OrgDate(start + timedelta(minutes=offset)) for offset in range(3)
    ]
    content = "\n".join(
        f"* Meeting\n  {timestamp}\n  :PROPERTIES:\n"
        f"  :UID: subhourly-event\n  :RRULE: {rule}\n  :END:"
        for timestamp in timestamps
    )

    agenda = OrgDateAgenda.from_str(content)

    assert agenda.dates["subhourly-event"] == timestamps
    assert all(
        timestamp._repeater is None
        for timestamp in agenda.dates["subhourly-event"]
    )
    assert agenda.get_rrulestr("subhourly-event") == rule


@pytest.mark.parametrize(
    ("frequency", "interval"), [("MINUTELY", 1), ("SECONDLY", 60)]
)
def test_list_exports_subhourly_occurrences(runner, frequency, interval):
    """Calendar export must retain minute-aligned subhourly occurrences."""
    start = datetime.combine(
        (datetime.now() + timedelta(days=1)).date(), time(10)
    )
    event = Event()
    event.add("uid", "subhourly-event")
    event.add("summary", "Subhourly meeting")
    event.add("dtstart", start)
    event.add("dtend", start + timedelta(minutes=1))
    event.add("rrule", {"freq": frequency, "interval": interval, "count": 3})
    calendar = ICalendar()
    calendar.add("version", "2.0")
    calendar.add("prodid", "-//khalorg tests//EN")
    calendar.add_component(event)
    event_file = Path(str(runner.calendars["one"])) / "subhourly-event.ics"
    event_file.write_bytes(calendar.to_ical())

    output = list_command(
        "one", khalorg_format=get_default_khalorg_format(), stop="3d"
    )
    agenda = OrgAgendaFile.from_str(output)

    assert len(agenda.items) == 1
    item = agenda.items[0]
    assert item.uid == "subhourly-event"
    assert [timestamp.start for timestamp in item.timestamps] == [
        start + timedelta(minutes=offset) for offset in range(3)
    ]
    assert all(timestamp._repeater is None for timestamp in item.timestamps)
