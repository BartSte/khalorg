"""Regression tests for monthly calendar recurrence exports."""

from datetime import date, datetime

import pytest
from khal.cli import main_khal

from khalorg.commands import list_command
from khalorg.helpers import get_default_khalorg_format
from khalorg.khal.calendar import Calendar
from khalorg.org.agenda_items import OrgAgendaFile
from khalorg.rrule import rrulestr_is_supported, rrulestr_to_org
from tests.helpers import khal_runner


@pytest.mark.parametrize(
    ("rule", "repeater"),
    [
        ("FREQ=MONTHLY", ("+", 1, "m")),
        ("FREQ=MONTHLY;BYMONTHDAY=15", ("+", 1, "m")),
        ("FREQ=MONTHLY;INTERVAL=2;BYMONTHDAY=1", ("+", 2, "m")),
        ("FREQ=MONTHLY;BYMONTHDAY=1,15", None),
        ("FREQ=MONTHLY;INTERVAL=2;BYMONTHDAY=1,15", None),
        ("FREQ=MONTHLY;BYMONTHDAY=1,-1", None),
    ],
)
def test_monthly_rule_conversion(rule, repeater):
    """Convert only monthly rules that fit a single org repeater."""
    assert rrulestr_is_supported(rule) is (repeater is not None)
    assert rrulestr_to_org(rule) == repeater


@pytest.fixture
def calendar_runner(tmpdir, monkeypatch):
    """Return a temporary calendar runner for export tests."""
    runner = khal_runner(tmpdir, monkeypatch)()

    def list_events(_calendar, args):
        result = runner.invoke(main_khal, ["list", "-df", "", *args])
        assert result.exit_code == 0, result.output
        return result.output

    monkeypatch.setattr(Calendar, "list_command", list_events)
    return runner


@pytest.mark.parametrize("all_day", [False, True])
@pytest.mark.parametrize(
    ("rule", "dates", "repeater"),
    [
        (
            "FREQ=MONTHLY;BYMONTHDAY=1,15",
            [(1, 1), (1, 15), (2, 1), (2, 15), (3, 1), (3, 15)],
            None,
        ),
        (
            "FREQ=MONTHLY;INTERVAL=2;BYMONTHDAY=1,15",
            [(1, 1), (1, 15), (3, 1), (3, 15)],
            None,
        ),
        ("FREQ=MONTHLY;BYMONTHDAY=1", [(1, 1)], ("+", 1, "m")),
    ],
)
def test_monthly_calendar_export(
    calendar_runner, all_day, rule, dates, repeater
):
    """Retain every occurrence when one repeater cannot describe the rule."""
    if all_day:
        times = "DTSTART;VALUE=DATE:20300101\nDTEND;VALUE=DATE:20300102"
    else:
        times = "DTSTART:20300101T100000\nDTEND:20300101T110000"
    calendar_runner.calendars["one"].join("monthly.ics").write(
        "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//khalorg tests//EN\n"
        f"BEGIN:VEVENT\nUID:monthly-series\n{times}\n"
        f"SUMMARY:Monthly meeting\nRRULE:{rule}\n"
        "END:VEVENT\nEND:VCALENDAR\n"
    )

    exported = list_command(
        "one",
        khalorg_format=get_default_khalorg_format(),
        start="2030-01-01 Tue",
        stop="2030-03-31 Sun",
    )
    agenda = OrgAgendaFile.from_str(exported)

    assert len(agenda.items) == 1
    item = agenda.items[0]
    assert item.uid == "monthly-series"
    expected_starts = [
        date(2030, month, day) if all_day else datetime(2030, month, day, 10)
        for month, day in dates
    ]
    assert [timestamp.start for timestamp in item.timestamps] == expected_starts
    assert all(timestamp._repeater == repeater for timestamp in item.timestamps)
