from datetime import date, datetime, timedelta
from test.helpers import (
    assert_event_created,
    assert_event_edited,
    khal_runner,
)
from typing import Callable, Generator

import pytest
from khal.cli import main_khal
from munch import Munch, munchify
from orgparse.date import OrgDate

from src.commands import _edit, _new
from src.khal_items import (
    Calendar,
)
from src.org_items import OrgAgendaItem

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

    def khal_new(_, args: list):
        runner.invoke(main_khal, ['new'] + args)

    monkeypatch.setattr(Calendar, 'new_item', khal_new)
    yield runner


_TEST_EVENT: dict = dict(
    summary='summary',
    description="hello,\n\n text.\n\nbye",
    properties={
        'ATTENDEES': 'test@test.com, test2@test.com',
        'CATEGORIES': 'category1, category2',
        'LOCATION': 'location1, location2',
        'URL': 'www.test.com'
    })


def test_edit(runner):
    """
    Test src.commands._new and src.commands._edit.

    Creates a new event with the bare minimal information. Later, the
    additional information is edited using the edit command. The result is
    asserted using the `khal list` command.

    Args:
    ----
        get_cli_runner: from the pytest fixture
    """
    org_item: OrgAgendaItem = get_org_item()

    _new('one', org_item)
    event = assert_event_created('one', org_item)
    org_item.properties['UID'] = event[0].uid  # UID needed for editing
    _edit('one', org_item)
    assert_event_edited(runner, 'one', org_item)


def get_org_item(delta: timedelta = timedelta(hours=1),
                 all_day: bool = False,
                 until: str = '',
                 repeater: tuple | None = None) -> OrgAgendaItem:
    """
    Returns an org_item that is used for testing.

    Returns
    -------
        an org agenda item used for test
    """
    start, end = get_start_end_now(delta=delta, all_day=all_day)
    test_event: Munch = munchify(_TEST_EVENT)  # type: ignore
    org_item: OrgAgendaItem = OrgAgendaItem(
        title=test_event.summary,
        timestamps=[OrgDate(start, end, repeater=repeater)],
        properties=dict(**test_event.properties),
        description=test_event.description
    )
    org_item.properties['UNTIL'] = until
    return org_item


def get_start_end_now(delta: timedelta = timedelta(hours=1),
                      all_day: bool = False
                      ) -> tuple[Time, Time]:
    """
    Get start and end datetime with a time difference of `delta`.

    Args:
    ----
        delta: timedelta, default is 1 hour

    Returns:
    -------
        the start and end times when planning an even now.

    """
    start: datetime = datetime.now()
    end: datetime = datetime.now() + delta

    if all_day:
        return datetime.date(start), datetime.date(end)
    else:
        start = start.replace(second=0, microsecond=0)
        end = end.replace(second=0, microsecond=0)
        return start, end


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
    """
    After adding a new event, its addendees are added. When running khal
    list, the attendees should be visible.
    """
    org_item: OrgAgendaItem = get_org_item(all_day=True)
    _new('one', org_item)
    event: list = assert_event_created('one', org_item)
    org_item.properties['UID'] = event[0].uid
    _edit('one', org_item)
    assert_event_edited(runner, 'one', org_item)


def test_edit_recurring(runner):
    """
    After adding a new event, its addendees are added. When running khal
    list, the attendees should be visible.
    """
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


def test_edit_recurring_twice(runner):
    """Edit an recurring items twice to ensure no events were corrupted by us."""
    days = 1
    calendar: Calendar = Calendar('one')
    until: date = datetime.today() + timedelta(days=days)
    org_item: OrgAgendaItem = test_edit_recurring(runner)
    org_item.properties['UNTIL'] = until.strftime(calendar.date_format)
    _edit('one', org_item, edit_dates=True)
    assert_event_edited(runner, 'one', org_item, count=days)
