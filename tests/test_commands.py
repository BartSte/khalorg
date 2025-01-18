from datetime import date, datetime, timedelta
import logging
from os.path import join
from tests import static
from tests.helpers import (
    assert_event_created,
    assert_event_deleted,
    assert_event_edited,
    get_module_path,
    get_org_item,
    khal_runner,
)
from typing import Callable, Generator

import pytest
from khal.cli import main_khal
from orgparse.date import OrgDate

from khalorg.commands import _delete, _edit, _new, delete, list_command, new
from khalorg.khal.calendar import Calendar
from khalorg.org.agenda_items import OrgAgendaItem

Time = datetime | date
FORMAT = '%Y-%m-%d %a %H:%M'


@pytest.fixture
def get_cli_runner(tmpdir, monkeypatch) -> Callable:
    return khal_runner(tmpdir, monkeypatch)


@pytest.fixture
def runner(get_cli_runner, monkeypatch) -> Generator:
    """
    Returns a test runnen that is created by CliRunner.

    The Calendar.new_item is monkeypatched to enable using the temporarly
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
        result = runner.invoke(main_khal, ['new'] + args)
        if result.exit_code:
            raise result.exception
        return result.output

    def khal_list(_, args: list):
        result = runner.invoke(main_khal, ['list', '-df', ''] + args)
        if result.exit_code:
            raise result.exception
        return result.output

    monkeypatch.setattr(Calendar, 'new_item', khal_new)
    monkeypatch.setattr(Calendar, 'list_command', khal_list)

    yield runner


def test_list(runner):
    """
    The list_command function is expected to retrun the same item as
    `expected`.
    """
    expected: OrgAgendaItem = get_org_item()
    _list_test(runner, expected)


def _list_test(runner, expected: OrgAgendaItem):
    format_file: str = join(get_module_path(static), 'khalorg_format_full.txt')
    with open(format_file) as f:
        khalorg_format: str = f.read()

    actual: OrgAgendaItem = OrgAgendaItem()
    new('one', org=str(expected))
    stdout: str = list_command('one', khalorg_format)
    actual.load_from_str(stdout)

    # UID and CALENDAR are changed in the process.
    expected.properties['UID'] = actual.properties['UID']
    expected.properties['CALENDAR'] = actual.properties['CALENDAR']
    expected.properties['RRULE'] = actual.properties['RRULE']

    logging.debug("khalorg_format: %s", khalorg_format)
    logging.debug("Stdout: %s", stdout)
    logging.debug("Expected: %s", expected)
    logging.debug("Actual: %s", actual)
    assert str(expected) == str(actual)
    # A recurring item should have a non empty rrule
    assert bool(actual.properties['RRULE']) == bool(expected.first_timestamp._repeater)  # noqa


def test_list_recurring(runner):
    """ List supported recurring items. """
    daily = [(1, 'd'), (2, 'd')]
    weekly = [(1, 'w'), (2, 'w')]
    monthly = [(1, 'm'), (2, 'm')]
    yearly = [(1, 'y'), (2, 'y')]
    for interval, freq in daily + weekly + monthly + yearly:
        expected: OrgAgendaItem = get_org_item(repeater=('+', interval, freq))
        _list_test(runner, expected)
        _delete('one', expected)


def test_list_allday(runner):
    """An all day event must be listed."""
    expected: OrgAgendaItem = get_org_item(all_day=True)
    _list_test(runner, expected)


def test_list_allday_recurring(runner):
    """All day recurring events must also be listed."""
    expected: OrgAgendaItem = get_org_item(all_day=True,
                                           repeater=('+', 1, 'm'))
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

    _new('one', org_item)
    event = assert_event_created('one', org_item)
    org_item.properties['UID'] = event[0].uid  # UID needed for editing
    _edit('one', org_item)
    assert_event_edited(runner, 'one', org_item)


def test_edit_change_time(runner):
    """
    Same as `test_edit` but now change the time.

    Args:
    ----
        runner: from the pytest fixture
    """
    org_item: OrgAgendaItem = get_org_item()

    _new('one', org_item)
    event = assert_event_created('one', org_item)

    start = org_item.first_timestamp.start + timedelta(days=1)
    end = org_item.first_timestamp.end + timedelta(days=1)
    org_item.timestamps = [OrgDate(start, end)]  # edit time

    org_item.properties['UID'] = event[0].uid  # UID needed for editing
    _edit('one', org_item)
    assert_event_edited(runner, 'one', org_item)


def test_edit_all_day(runner):
    """Create a new all day event and edit it."""
    org_item: OrgAgendaItem = get_org_item(all_day=True)
    _new('one', org_item)
    event: list = assert_event_created('one', org_item)
    org_item.properties['UID'] = event[0].uid
    _edit('one', org_item)
    assert_event_edited(runner, 'one', org_item)


def test_edit_recurring(runner):
    """Create a new recurring event and edit it."""
    _edit_recurring(runner)


def _edit_recurring(runner):
    days = 7
    calendar: Calendar = Calendar('one')
    until: date = datetime.today() + timedelta(days=days)
    org_item: OrgAgendaItem = get_org_item(
        until=until.strftime(calendar.date_format),
        repeater=('+', 1, 'd'))
    _new('one', org_item)
    events: list = assert_event_created('one', org_item, recurring=True)

    org_item.properties['UID'] = events[0].uid
    _edit('one', org_item, edit_dates=True)
    assert_event_edited(runner, 'one', org_item, count=days)
    return org_item


def test_edit_all_day_recurring(runner):
    """Create a new all day recurring event and edit it."""
    _edit_all_day_recurring(runner)


def _edit_all_day_recurring(runner):
    days = 7
    calendar = Calendar('one')
    until: date = datetime.today() + timedelta(days=days - 1)
    org_item: OrgAgendaItem = get_org_item(
        all_day=True,
        until=until.strftime(calendar.date_format),
        repeater=('+', 1, 'd'))
    _new('one', org_item)
    event: list = assert_event_created('one', org_item, recurring=True)
    org_item.properties['UID'] = event[0].uid
    _edit('one', org_item)
    assert_event_edited(runner, 'one', org_item, count=7)
    return org_item


def test_edit_recurring_twice(runner):
    """
    Edit an recurring items twice to ensure no events were corrupted by
    us.
    """
    days = 1
    calendar: Calendar = Calendar('one')
    until: date = datetime.today() + timedelta(days=days)
    org_item: OrgAgendaItem = _edit_recurring(runner)
    org_item.properties['UNTIL'] = until.strftime(calendar.date_format)
    _edit('one', org_item, edit_dates=True)
    assert_event_edited(runner, 'one', org_item, count=days)


def test_edit_all_day_recurring_twice(runner):
    """
    Edit an recurring allday item twice to ensure no events were corrupted
    by us.
    """
    days = 1
    calendar: Calendar = Calendar('one')
    until: date = datetime.today() + timedelta(days=days - 1)
    org_item: OrgAgendaItem = _edit_all_day_recurring(runner)
    org_item.properties['UNTIL'] = until.strftime(calendar.date_format)
    _edit('one', org_item, edit_dates=True)
    assert_event_edited(runner, 'one', org_item, count=days)


def test_delete(runner):
    """After creating an event, the `delete` command should delete it."""
    expected: OrgAgendaItem = get_org_item()
    new('one', org=str(expected))
    events = assert_event_created('one', expected)
    expected.properties['UID'] = str(events[0].uid)
    delete('one', org=str(expected))
    assert_event_deleted('one', expected)
