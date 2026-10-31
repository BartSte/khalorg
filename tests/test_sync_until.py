"""Regression tests for recurrence end dates in synchronization."""

from datetime import date, datetime, timedelta
from pathlib import Path

import pytest
from orgparse.date import OrgDate

from khalorg import paths
from khalorg.commands import _edit, _list, sync
from khalorg.org.agenda_items import OrgAgendaFile, OrgAgendaItem
from khalorg.rrule import rrulestr_to_rrule
from tests.test_commands import get_cli_runner as get_cli_runner
from tests.test_commands import runner as runner


@pytest.fixture(autouse=True)
def default_output_format(monkeypatch, tmp_path: Path):
    """Keep these tests independent of the user's output template."""
    monkeypatch.setattr(paths, "format", str(tmp_path / "missing-format"))


def write_recurring_org(org_file: Path, all_day: bool = False) -> str:
    """Write a weekly event with an explicit end date for recurrence."""
    start = datetime.combine(
        date.today() + timedelta(days=1), datetime.min.time()
    )
    start += timedelta(hours=10)
    if all_day:
        timestamp = OrgDate(start.date(), repeater=("+", 1, "w"))
        until = OrgDate((start + timedelta(days=28)).date(), active=False)
    else:
        timestamp = OrgDate(
            start, start + timedelta(hours=1), repeater=("+", 1, "w")
        )
        until = OrgDate(start + timedelta(days=28), active=False)
    org_file.write_text(
        f"* Weekly meeting\n  {timestamp}\n  :PROPERTIES:\n"
        f"  :UNTIL: {until}\n  :END:\n"
    )
    return str(until)


@pytest.mark.parametrize("all_day", [False, True])
def test_sync_preserves_new_recurrence_end(
    runner, tmp_path: Path, all_day: bool
):
    """A new event must retain its end date in khal and both org files."""
    org_file = tmp_path / "events.org"
    state_dir = tmp_path / "state"
    write_recurring_org(org_file, all_day)
    expected_until = OrgAgendaFile.from_path(org_file).items[0].until.start

    sync("one", org_file, state_dir, stop="60d")
    sync("one", org_file, state_dir, stop="60d")

    event = _list("one", stop="60d").items[0]
    rule = rrulestr_to_rrule(event.properties["RRULE"])
    assert rule._until is not None
    expected_date = (
        expected_until.date()
        if isinstance(expected_until, datetime)
        else expected_until
    )
    assert rule._until.date() == expected_date
    for agenda_file in (org_file, state_dir / "one.org"):
        assert (
            OrgAgendaFile.from_path(agenda_file).items[0].until.start
            == expected_until
        )


@pytest.mark.parametrize("end_date_edit", ["extend", "clear", "remove"])
@pytest.mark.parametrize("conflict", [False, True])
def test_sync_preserves_recurrence_end_edits(
    runner, tmp_path: Path, end_date_edit: str, conflict: bool
):
    """Org changes must update or clear the end date without losing edits."""
    org_file = tmp_path / "events.org"
    state_dir = tmp_path / "state"
    original_until = write_recurring_org(org_file)
    sync("one", org_file, state_dir, stop="60d")
    original = OrgAgendaFile.from_path(org_file).items[0]
    if conflict:
        original.title = "Remote edit"
        _edit("one", original)

    if end_date_edit == "extend":
        until = str(
            OrgDate(original.until.start + timedelta(days=14), active=False)
        )
        content = org_file.read_text().replace(original_until, until)
    elif end_date_edit == "clear":
        until = ""
        content = org_file.read_text().replace(original_until, "")
    else:
        until = ""
        content = "\n".join(
            line
            for line in org_file.read_text().splitlines()
            if not line.strip().startswith(":UNTIL:")
        )
    org_file.write_text(content.replace("Weekly meeting", "Local edit"))

    sync(
        "one",
        org_file,
        state_dir,
        stop="60d",
        edit_dates=True,
        conflict_resolution="org",
    )

    event = _list("one", stop="60d").items[0]
    assert event.title == "Local edit"
    rule = rrulestr_to_rrule(event.properties["RRULE"])
    if until:
        assert rule._until is not None
        assert (
            rule._until.date()
            == (original.until.start + timedelta(days=14)).date()
        )
    else:
        assert rule._until is None
    for agenda_file in (org_file, state_dir / "one.org"):
        assert (
            OrgAgendaFile.from_path(agenda_file).items[0].properties["UNTIL"]
            == until
        )


@pytest.mark.parametrize("rrule", ["", "FREQ=WEEKLY;UNTIL=20300101T100000Z"])
@pytest.mark.parametrize("until", ["", "[2030-02-01 Fri 10:00]"])
def test_format_preserves_explicit_until(rrule: str, until: str):
    """An explicit org end date takes precedence over a stale RRULE."""
    item = OrgAgendaItem(properties={"UNTIL": until, "RRULE": rrule})

    assert format(item, "{until_rrule}") == until


def test_calendar_export_derives_until_from_rrule():
    """Calendar imports must use the actual RRULE end date."""
    agenda = OrgAgendaFile.from_str(
        "* Weekly meeting\n  <2030-01-01 Tue 10:00-11:00>\n"
        "  :PROPERTIES:\n  :UID: weekly\n  :UNTIL:\n"
        "  :RRULE: FREQ=WEEKLY;UNTIL=20300201T100000Z\n  :END:\n"
    )

    agenda.apply_rrules()

    assert format(agenda.items[0], "{until_rrule}") == "[2030-02-01 Fri 10:00]"
