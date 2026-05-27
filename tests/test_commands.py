from datetime import date, datetime, timedelta
from pathlib import Path
import copy
import logging
from os.path import join
from tests import static
from tests.helpers import (
    assert_event_created,
    assert_event_deleted,
    assert_event_edited,
    get_module_path,
    get_org_item,
    get_start_end,
    khal_runner,
)
from typing import Callable, Generator

import pytest
from khal.cli import main_khal
from orgparse.date import OrgDate

from khalorg.commands import (
    _delete,
    _edit,
    _new,
    delete,
    list_command,
    new,
    sync,
)
from khalorg.khal.calendar import Calendar
from khalorg.org.agenda_items import OrgAgendaItem

Time = datetime | date
FORMAT = "%Y-%m-%d %a %H:%M"


@pytest.fixture
def get_cli_runner(tmpdir, monkeypatch) -> Callable:
    return khal_runner(tmpdir, monkeypatch)


@pytest.fixture
def runner(get_cli_runner, monkeypatch) -> Generator:
    """
    Returns a test runner that is created by CliRunner.

    The Calendar.new_item is monkeypatched to enable using the temporarily
    created calendar.

    Args:
    ----
        get_cli_runner: fixture
        monkeypatch: fixture

    Returns:
    -------
        test runner
    """
    runner = get_cli_runner()

    def khal_new(_, args: list) -> str:
        result = runner.invoke(main_khal, ["new"] + args)
        if result.exit_code:
            raise result.exception
        return result.output

    def khal_list(_, args: list):
        result = runner.invoke(main_khal, ["list", "-df", ""] + args)
        if result.exit_code:
            raise result.exception
        return result.output

    monkeypatch.setattr(Calendar, "new_item", khal_new)
    monkeypatch.setattr(Calendar, "list_command", khal_list)

    yield runner


def test_list(runner):
    """
    The list_command function is expected to return the same item as
    `expected`.
    """
    expected: OrgAgendaItem = get_org_item()
    _list_test(runner, expected)


def _list_test(runner, expected: OrgAgendaItem):
    format_file: str = join(get_module_path(static), "khalorg_format_full.txt")
    with open(format_file) as f:
        khalorg_format: str = f.read()

    actual: OrgAgendaItem = OrgAgendaItem()
    new("one", org=str(expected))
    stdout: str = list_command("one", khalorg_format)
    actual.load_from_str(stdout)

    # UID and CALENDAR are changed in the process.
    expected.properties["UID"] = actual.properties["UID"]
    expected.properties["CALENDAR"] = actual.properties["CALENDAR"]
    expected.properties["RRULE"] = actual.properties["RRULE"]

    logging.debug("khalorg_format: %s", khalorg_format)
    logging.debug("Stdout: %s", stdout)
    logging.debug("Expected: %s", expected)
    logging.debug("Actual: %s", actual)
    assert str(expected) == str(actual)
    # A recurring item should have a non empty rrule
    assert bool(actual.properties["RRULE"]) == bool(
        expected.first_timestamp._repeater
    )  # noqa


def test_list_recurring(runner):
    """List supported recurring items."""
    daily = [(1, "d"), (2, "d")]
    weekly = [(1, "w"), (2, "w")]
    monthly = [(1, "m"), (2, "m")]
    yearly = [(1, "y"), (2, "y")]
    for interval, freq in daily + weekly + monthly + yearly:
        expected: OrgAgendaItem = get_org_item(repeater=("+", interval, freq))
        _list_test(runner, expected)
        _delete("one", expected)


def test_list_allday(runner):
    """An all day event must be listed."""
    expected: OrgAgendaItem = get_org_item(all_day=True)
    _list_test(runner, expected)


def test_list_allday_recurring(runner):
    """All day recurring events must also be listed."""
    expected: OrgAgendaItem = get_org_item(all_day=True, repeater=("+", 1, "m"))
    _list_test(runner, expected)


def test_edit(runner):
    """
    Test khalorg.commands._new and khalorg.commands._edit.

    Creates a new event with the bare minimal information. Later, the
    additional information is edited using the edit command. The result is
    asserted using the `khal list` command.

    Args:
    ----
        runner: from the pytest fixture
    """
    org_item: OrgAgendaItem = get_org_item()

    _new("one", org_item)
    event = assert_event_created("one", org_item)
    org_item.properties["UID"] = event[0].uid  # UID needed for editing
    _edit("one", org_item)
    assert_event_edited(runner, "one", org_item)


def test_edit_change_time(runner):
    """
    Same as `test_edit` but now change the time.

    Args:
    ----
        runner: from the pytest fixture
    """
    org_item: OrgAgendaItem = get_org_item()

    _new("one", org_item)
    event = assert_event_created("one", org_item)

    start = org_item.first_timestamp.start + timedelta(days=1)
    end = org_item.first_timestamp.end + timedelta(days=1)
    org_item.timestamps = [OrgDate(start, end)]  # edit time

    org_item.properties["UID"] = event[0].uid  # UID needed for editing
    _edit("one", org_item)
    assert_event_edited(runner, "one", org_item)


def test_edit_all_day(runner):
    """Create a new all day event and edit it."""
    org_item: OrgAgendaItem = get_org_item(all_day=True)
    _new("one", org_item)
    event: list = assert_event_created("one", org_item)
    org_item.properties["UID"] = event[0].uid
    _edit("one", org_item)
    assert_event_edited(runner, "one", org_item)


def test_edit_recurring(runner):
    """Create a new recurring event and edit it."""
    _edit_recurring(runner)


def _edit_recurring(runner):
    days = 7
    calendar: Calendar = Calendar("one")
    until: date = datetime.today() + timedelta(days=days)
    org_item: OrgAgendaItem = get_org_item(
        until=until.strftime(calendar.date_format), repeater=("+", 1, "d")
    )
    _new("one", org_item)
    events: list = assert_event_created("one", org_item, recurring=True)

    org_item.properties["UID"] = events[0].uid
    _edit("one", org_item, edit_dates=True)
    assert_event_edited(runner, "one", org_item, count=days)
    return org_item


def test_edit_all_day_recurring(runner):
    """Create a new all day recurring event and edit it."""
    _edit_all_day_recurring(runner)


def _edit_all_day_recurring(runner):
    days = 7
    calendar = Calendar("one")
    until: date = datetime.today() + timedelta(days=days - 1)
    org_item: OrgAgendaItem = get_org_item(
        all_day=True,
        until=until.strftime(calendar.date_format),
        repeater=("+", 1, "d"),
    )
    _new("one", org_item)
    event: list = assert_event_created("one", org_item, recurring=True)
    org_item.properties["UID"] = event[0].uid
    _edit("one", org_item)
    assert_event_edited(runner, "one", org_item, count=7)
    return org_item


def test_edit_recurring_twice(runner):
    """
    Edit an recurring items twice to ensure no events were corrupted by
    us.
    """
    days = 1
    calendar: Calendar = Calendar("one")
    until: date = datetime.today() + timedelta(days=days)
    org_item: OrgAgendaItem = _edit_recurring(runner)
    org_item.properties["UNTIL"] = until.strftime(calendar.date_format)
    _edit("one", org_item, edit_dates=True)
    assert_event_edited(runner, "one", org_item, count=days)


def test_edit_all_day_recurring_twice(runner):
    """
    Edit an recurring allday item twice to ensure no events were corrupted
    by us.
    """
    days = 1
    calendar: Calendar = Calendar("one")
    until: date = datetime.today() + timedelta(days=days - 1)
    org_item: OrgAgendaItem = _edit_all_day_recurring(runner)
    org_item.properties["UNTIL"] = until.strftime(calendar.date_format)
    _edit("one", org_item, edit_dates=True)
    assert_event_edited(runner, "one", org_item, count=days)


def test_delete(runner):
    """After creating an event, the `delete` command should delete it."""
    expected: OrgAgendaItem = get_org_item()
    new("one", org=str(expected))
    events = assert_event_created("one", expected)
    expected.properties["UID"] = str(events[0].uid)
    delete("one", org=str(expected))
    assert_event_deleted("one", expected)


def _sync_test_local(org_file: Path, expected: OrgAgendaItem) -> None:
    assert org_file.exists()
    actual: OrgAgendaItem = OrgAgendaItem()
    actual.load_from_str(org_file.read_text())

    # UID and CALENDAR are changed in the process.
    expected.properties["UID"] = actual.properties["UID"]
    expected.properties["CALENDAR"] = actual.properties["CALENDAR"]

    logging.debug("Expected: %s", expected)
    logging.debug("Actual: %s", actual)
    assert str(expected) == str(actual)


def _sync_test_remote(expected: OrgAgendaItem) -> None:
    format_file: str = join(get_module_path(static), "khalorg_format_full.txt")
    with open(format_file) as f:
        khalorg_format: str = f.read()

    actual: OrgAgendaItem = OrgAgendaItem()
    stdout: str = list_command("one", khalorg_format)
    actual.load_from_str(stdout)

    # UID and CALENDAR are changed in the process.
    expected.properties["UID"] = actual.properties["UID"]
    expected.properties["CALENDAR"] = actual.properties["CALENDAR"]

    logging.debug("khalorg_format: %s", khalorg_format)
    logging.debug("Stdout: %s", stdout)
    logging.debug("Expected: %s", expected)
    logging.debug("Actual: %s", actual)
    assert str(expected) == str(actual)


def test_sync_pushes_new_events(runner, tmp_path: Path):
    """Sync will push org new events to khal."""
    org_file = tmp_path / "file.org"
    state_dir = tmp_path / "state"
    start, end = get_start_end(delta=timedelta(hours=1))
    date = OrgDate(start, end)
    org_file.write_text(f"""* new event
  {str(date)}
""")
    expected: OrgAgendaItem = OrgAgendaItem(
        title="new event", timestamps=[date]
    )

    sync("one", org_file, state_dir)

    _sync_test_local(org_file, expected)
    _sync_test_remote(expected)


def test_sync_doesnt_push_new_events_on_dry_run(runner, tmp_path: Path):
    """Sync will push org new events to khal."""
    org_file = tmp_path / "file.org"
    state_dir = tmp_path / "state"
    start, end = get_start_end(delta=timedelta(hours=1))
    date = OrgDate(start, end)
    org_file.write_text(f"""* new event
  {str(date)}
""")
    expected: OrgAgendaItem = OrgAgendaItem(
        title="new event", timestamps=[date]
    )

    sync("one", org_file, state_dir, dry_run=True)

    format_file: str = join(get_module_path(static), "khalorg_format_full.txt")
    with open(format_file) as f:
        khalorg_format: str = f.read()

    assert list_command("one", khalorg_format) == ""


def test_sync_pulls_new_events(runner, tmp_path: Path):
    """Sync will pull org new events from khal."""
    org_file = tmp_path / "file.org"
    state_dir = tmp_path / "state"
    expected: OrgAgendaItem = get_org_item()
    new("one", org=str(expected))

    sync("one", org_file, state_dir)

    _sync_test_local(org_file, expected)
    _sync_test_remote(expected)


def test_sync_doesnt_pull_new_events_on_dry_run(runner, tmp_path: Path):
    """Sync will pull org new events from khal."""
    org_file = tmp_path / "file.org"
    state_dir = tmp_path / "state"
    expected: OrgAgendaItem = get_org_item()
    new("one", org=str(expected))

    sync("one", org_file, state_dir, dry_run=True)

    assert org_file.read_text() == ""
    _sync_test_remote(expected)


@pytest.mark.parametrize("dry_run", [False, True])
def test_sync_pushes_local_edits(runner, tmp_path: Path, dry_run: bool):
    """Sync will push org edits to khal events; dry_run skips the remote push."""
    org_file = tmp_path / "file.org"
    state_dir = tmp_path / "state"
    initial: OrgAgendaItem = get_org_item()
    new("one", org=str(initial))
    sync("one", org_file, state_dir)
    expected = copy.deepcopy(initial)
    expected.title = "edited summary"
    content = org_file.read_text().replace("summary", expected.title)
    org_file.write_text(content)

    sync("one", org_file, state_dir, dry_run=dry_run)

    _sync_test_local(org_file, expected)
    _sync_test_remote(initial if dry_run else expected)


@pytest.mark.parametrize("dry_run", [False, True])
def test_sync_pulls_remote_edits(runner, tmp_path: Path, dry_run: bool):
    """Sync will pull remote edits into the org file; dry_run skips the local write."""
    org_file = tmp_path / "file.org"
    state_dir = tmp_path / "state"
    khal_calendar: Calendar = Calendar("one")
    initial: OrgAgendaItem = get_org_item()
    new("one", org=str(initial))
    new_item_uid = str(
        khal_calendar.get_events_no_uid(
            summary_wanted=initial.title,
            start_wanted=initial.timestamps[0].start,
            end_wanted=initial.timestamps[0].end,
        )[0].uid
    )
    sync("one", org_file, state_dir)
    expected = copy.deepcopy(initial)
    expected.title = "updated summary"
    expected.properties["UID"] = new_item_uid
    _edit("one", expected)
    _sync_test_remote(expected)

    sync("one", org_file, state_dir, dry_run=dry_run)

    _sync_test_remote(expected)
    _sync_test_local(org_file, initial if dry_run else expected)


def test_sync_solves_conflicts_edits_favoring_khal_by_default(
    runner, tmp_path: Path
):
    """If event has changed both in org and khal, favour khal by default."""
    org_file = tmp_path / "file.org"
    state_dir = tmp_path / "state"
    khal_calendar: Calendar = Calendar("one")
    initial: OrgAgendaItem = get_org_item()
    new("one", org=str(initial))
    new_item_uid = str(
        khal_calendar.get_events_no_uid(
            summary_wanted=initial.title,
            start_wanted=initial.timestamps[0].start,
            end_wanted=initial.timestamps[0].end,
        )[0].uid
    )
    sync("one", org_file, state_dir)
    expected = copy.deepcopy(initial)
    expected.title = "khal edited summary"
    expected.properties["UID"] = new_item_uid
    _edit("one", expected)
    _sync_test_remote(expected)
    local_changes = org_file.read_text().replace(
        "summary", "org edited summary"
    )
    org_file.write_text(local_changes)

    sync("one", org_file, state_dir)

    _sync_test_remote(expected)
    _sync_test_local(org_file, expected)


def test_sync_doesnt_solve_conflicts_edits_favoring_khal_by_default_on_dry_run(
    runner, tmp_path: Path
):
    """If event has changed both in org and khal, favour khal by default."""
    org_file = tmp_path / "file.org"
    state_dir = tmp_path / "state"
    khal_calendar: Calendar = Calendar("one")
    initial: OrgAgendaItem = get_org_item()
    new("one", org=str(initial))
    new_item_uid = str(
        khal_calendar.get_events_no_uid(
            summary_wanted=initial.title,
            start_wanted=initial.timestamps[0].start,
            end_wanted=initial.timestamps[0].end,
        )[0].uid
    )
    sync("one", org_file, state_dir)
    expected = copy.deepcopy(initial)
    expected.title = "khal edited summary"
    expected.properties["UID"] = new_item_uid
    _edit("one", expected)
    _sync_test_remote(expected)
    local_changes = org_file.read_text().replace(
        "summary", "org edited summary"
    )
    org_file.write_text(local_changes)

    sync("one", org_file, state_dir, dry_run=True)

    _sync_test_remote(expected)
    assert org_file.read_text() == local_changes


@pytest.mark.parametrize("dry_run", [False, True])
def test_sync_solves_conflicts_edits_favoring_org_by_choice(
    runner, tmp_path: Path, dry_run: bool
):
    """Conflict with org wins; dry_run skips pushing org's version to remote."""
    org_file = tmp_path / "file.org"
    state_dir = tmp_path / "state"
    khal_calendar: Calendar = Calendar("one")
    initial: OrgAgendaItem = get_org_item()
    new("one", org=str(initial))
    new_item_uid = str(
        khal_calendar.get_events_no_uid(
            summary_wanted=initial.title,
            start_wanted=initial.timestamps[0].start,
            end_wanted=initial.timestamps[0].end,
        )[0].uid
    )
    sync("one", org_file, state_dir)
    remote_edit = copy.deepcopy(initial)
    remote_edit.title = "khal edited summary"
    remote_edit.properties["UID"] = new_item_uid
    _edit("one", remote_edit)
    _sync_test_remote(remote_edit)
    local_changes = org_file.read_text().replace("summary", "org edited summary")
    expected = copy.deepcopy(initial)
    expected.title = "org edited summary"
    org_file.write_text(local_changes)

    sync("one", org_file, state_dir, conflict_resolution="org", dry_run=dry_run)

    _sync_test_remote(remote_edit if dry_run else expected)
    _sync_test_local(org_file, expected)


def test_sync_deletes_local_removed_events(runner, tmp_path: Path):
    """If a synced event is removed from org, it's removed from the remote"""
    org_file = tmp_path / "file.org"
    state_dir = tmp_path / "state"
    khal_calendar: Calendar = Calendar("one")
    initial: OrgAgendaItem = get_org_item()
    new("one", org=str(initial))
    new_item_uid = str(
        khal_calendar.get_events_no_uid(
            summary_wanted=initial.title,
            start_wanted=initial.timestamps[0].start,
            end_wanted=initial.timestamps[0].end,
        )[0].uid
    )
    sync("one", org_file, state_dir)
    org_file.write_text("")

    sync("one", org_file, state_dir, delete_on_sync=True)

    assert org_file.read_text() == ""
    assert len(khal_calendar.get_events(new_item_uid)) == 0


def test_sync_doesnt_delete_local_removed_events_on_dry_run(
    runner, tmp_path: Path
):
    """If a synced event is removed from org, it's removed from the remote"""
    org_file = tmp_path / "file.org"
    state_dir = tmp_path / "state"
    khal_calendar: Calendar = Calendar("one")
    initial: OrgAgendaItem = get_org_item()
    new("one", org=str(initial))
    new_item_uid = str(
        khal_calendar.get_events_no_uid(
            summary_wanted=initial.title,
            start_wanted=initial.timestamps[0].start,
            end_wanted=initial.timestamps[0].end,
        )[0].uid
    )
    sync("one", org_file, state_dir)
    org_file.write_text("")

    sync("one", org_file, state_dir, delete_on_sync=True, dry_run=True)

    assert org_file.read_text() == ""
    assert len(khal_calendar.get_events(new_item_uid)) == 1


def test_sync_doesnt_delete_local_removed_events_by_default(
    runner, tmp_path: Path
):
    """If a synced event is removed from org, it's removed from the remote"""
    org_file = tmp_path / "file.org"
    state_dir = tmp_path / "state"
    khal_calendar: Calendar = Calendar("one")
    initial: OrgAgendaItem = get_org_item()
    new("one", org=str(initial))
    new_item_uid = str(
        khal_calendar.get_events_no_uid(
            summary_wanted=initial.title,
            start_wanted=initial.timestamps[0].start,
            end_wanted=initial.timestamps[0].end,
        )[0].uid
    )
    sync("one", org_file, state_dir)
    org_file.write_text("")

    sync("one", org_file, state_dir)

    assert org_file.read_text() == ""
    assert len(khal_calendar.get_events(new_item_uid)) == 1


def test_sync_deletes_remote_removed_events(runner, tmp_path: Path):
    """If a synced event is removed from khal, it's removed from the local"""
    org_file = tmp_path / "file.org"
    state_dir = tmp_path / "state"
    khal_calendar: Calendar = Calendar("one")
    initial: OrgAgendaItem = get_org_item()
    new("one", org=str(initial))
    new_item_uid = str(
        khal_calendar.get_events_no_uid(
            summary_wanted=initial.title,
            start_wanted=initial.timestamps[0].start,
            end_wanted=initial.timestamps[0].end,
        )[0].uid
    )
    initial.properties["UID"] = new_item_uid
    sync("one", org_file, state_dir)
    delete("one", org=str(initial))

    sync("one", org_file, state_dir, delete_on_sync=True)

    assert len(khal_calendar.get_events(new_item_uid)) == 0
    assert org_file.read_text() == ""


def test_sync_doesnt_delete_remote_removed_events_on_dry_run(
    runner, tmp_path: Path
):
    """If a synced event is removed from khal, it's removed from the local"""
    org_file = tmp_path / "file.org"
    state_dir = tmp_path / "state"
    khal_calendar: Calendar = Calendar("one")
    initial: OrgAgendaItem = get_org_item()
    new("one", org=str(initial))
    new_item_uid = str(
        khal_calendar.get_events_no_uid(
            summary_wanted=initial.title,
            start_wanted=initial.timestamps[0].start,
            end_wanted=initial.timestamps[0].end,
        )[0].uid
    )
    initial.properties["UID"] = new_item_uid
    sync("one", org_file, state_dir)
    delete("one", org=str(initial))

    sync("one", org_file, state_dir, delete_on_sync=True, dry_run=True)

    assert len(khal_calendar.get_events(new_item_uid)) == 0
    _sync_test_local(org_file, initial)


def test_sync_doesnt_delete_remote_removed_events_by_default(
    runner, tmp_path: Path
):
    """If a synced event is removed from khal, it's removed from the local"""
    org_file = tmp_path / "file.org"
    state_dir = tmp_path / "state"
    khal_calendar: Calendar = Calendar("one")
    initial: OrgAgendaItem = get_org_item()
    new("one", org=str(initial))
    new_item_uid = str(
        khal_calendar.get_events_no_uid(
            summary_wanted=initial.title,
            start_wanted=initial.timestamps[0].start,
            end_wanted=initial.timestamps[0].end,
        )[0].uid
    )
    initial.properties["UID"] = new_item_uid
    sync("one", org_file, state_dir)
    delete("one", org=str(initial))

    sync("one", org_file, state_dir)

    assert len(khal_calendar.get_events(new_item_uid)) == 0
    _sync_test_local(org_file, initial)
