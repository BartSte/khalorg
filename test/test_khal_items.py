from datetime import date, datetime, timedelta
from test.agenda_items import AllDay, Recurring, Valid
from test.helpers import (
    assert_event_created,
    assert_event_edited,
    create_event,
    edit_event,
    get_test_config,
    khal_runner,
)
from typing import Callable
from unittest import TestCase
from unittest.mock import patch

import pytest
from click.testing import CliRunner
from khal.cli import main_khal
from khal.controllers import Event
from khal.khalendar import CalendarCollection
from munch import Munch, munchify
from orgparse.date import OrgDate

from src.khal_items import (
    Calendar,
    NewArgs,
    get_calendar_collection,
)
from src.org_items import OrgAgendaItem

FORMAT = '%Y-%m-%d %a %H:%M'


class Mixin:

    def setUp(self) -> None:
        args: list = Valid.get_args()
        self.agenda_item: OrgAgendaItem = OrgAgendaItem(*args)
        self.calendar = Calendar('test_calendar')


class TestCalendar(Mixin, TestCase):

    module: str = 'src.khal_items.find_configuration_file'

    @patch(module, return_value=get_test_config())
    def test_datetime_format(self, _):
        """The `datetime_format` must coincide. """
        self.assertEqual(self.calendar.datetime_format, '%Y-%m-%d %a %H:%M')


class TestArgs(Mixin, TestCase):

    def test_load_from_org(self):
        """
        When loaded from the org file valid.org, the resulting cli
        args must be the same as: Valid.command_line_args
        .
        """
        actual: NewArgs = NewArgs()
        actual.load_from_org(self.agenda_item)
        expected: dict = Valid.command_line_args
        message: str = (
            f'\nActual: {actual}\n Expected: {expected}'
        )
        self.assertEqual(actual, expected, msg=message)

    def test_load_from_org_recurring(self):
        """ Same as test_load_from_org but then with a recurring time stamp."""
        args: list = Recurring.get_args()
        agenda_item: OrgAgendaItem = OrgAgendaItem(*args)
        actual: NewArgs = NewArgs()
        actual.load_from_org(agenda_item)
        expected: dict = Recurring.command_line_args
        self.assertEqual(actual, expected)

    def test_load_from_org_all_day_event(self):
        """
        Test case for loading an all-day event from Org AgendaItem.

        This test case verifies that the method `load_from_org` of the
        `NewArgs` class is able to load an all-day event from an
        `OrgAgendaItem` object and produce the expected output. The test checks
        whether the loaded event matches the expected event.

        Raises
        ------
            AssertionError: If the loaded event does not match the expected
            event.

        """
        args: list = AllDay.get_args()
        agenda_item: OrgAgendaItem = OrgAgendaItem(*args)
        actual: NewArgs = NewArgs()
        actual.load_from_org(agenda_item)
        expected: dict = AllDay.command_line_args
        message: str = (
            f'\n\nActual: {actual}\n\nExpected: {expected}'
        )
        self.assertEqual(actual, expected, msg=message)

    def test_optional(self):
        """ When adding an option, it can be retrieved using Args.optional. """
        key = '--url'
        value: str = 'www.test.com'
        args: NewArgs = NewArgs()
        args[key] = value
        self.assertEqual(value, args.optional[key])

    def test_positional(self):
        """
        When adding an positional arg, it can be retrieved using
        Args.optional.
        """
        key = 'foo'
        value: str = 'bar'
        args: NewArgs = NewArgs()
        args[key] = value
        self.assertEqual(value, args.positional[key])

    def test_as_list(self):
        """
        Args.as_list contatinates all Args in a list. The dictionary key of
        an option is prepended before its value. Of the positional args, only
        its value is retained (obviously). Later, all arguments are split based
        on a whitespace. Statements surrounded by quotes are not (yet)
        supported.
        """
        args: NewArgs = NewArgs()
        args['--url'] = 'www.test.com'
        args['--until'] = '2024-01-01 Mon 01:00'
        args['start'] = datetime(2023, 1, 1).strftime(FORMAT)

        expected: list = [
            '--url',
            'www.test.com',
            '--until',
            '2024-01-01 Mon 01:00',
            '2023-01-01 Sun 00:00']

        actual: list = args.as_list()
        self.assertEqual(actual, expected)


@pytest.fixture
def get_cli_runner(tmpdir, monkeypatch) -> Callable:
    """
    `khal_runner` was borrowd from the `khal` repo at:
    https://github.com/pimutils/khal/blob/master/tests/cli_test.py.

    Args:
    ----
        tmpdir: build-in pytest fixture for temporary directories
        monkeypatch: build-in pytest fixture for patching.

    Returns
    -------
        a test runner function

    """
    return khal_runner(tmpdir, monkeypatch)


def test_get_calendar(get_cli_runner):
    """Must be able to find a calendar collection."""
    get_cli_runner()
    collection: CalendarCollection = get_calendar_collection('one')
    assert isinstance(collection, CalendarCollection)


def test_get_calendar_no_config(get_cli_runner):
    """
    Must be able to find a calendar collection. Even if no configuration
    file can be found.
    """
    from src import khal_items
    khal_items.find_configuration_file = lambda *_: None

    get_cli_runner()
    collection: CalendarCollection = get_calendar_collection('noneexisting')
    assert isinstance(collection, CalendarCollection)


def test_empty_calendar(get_cli_runner):
    runner = get_cli_runner()
    result = runner.invoke(main_khal, ['list'])
    assert result.output == ''
    assert not result.exception


_TEST_EVENT: dict = dict(
    summary='summary',
    description="hello,\n\n text.\n\nbye",
    properties={
        'ATTENDEES': 'test@test.com, test2@test.com',
        'CATEGORIES': 'category1, category2',
        'LOCATION': 'location1, location2',
        'URL': 'www.test.com'
    })


def test_calendar_edit_item(get_cli_runner: Callable):
    """Test Calendar.edit_item.

    Creates a new event with the bare minimal information. Later, the
    additional information is edited using the edit command. The result is
    asserted using the `khal list` command.

    Args:
    ----
        get_cli_runner:
    """
    test_event: Munch = munchify(_TEST_EVENT)  # type: ignore
    runner: CliRunner = get_cli_runner()

    start: datetime = datetime.now()
    end: datetime = datetime.now() + timedelta(hours=1)
    start = start.replace(second=0, microsecond=0)
    end = end.replace(second=0, microsecond=0)

    start_new: datetime = start + timedelta(days=1)
    end_new: datetime = end + timedelta(days=1)

    org_item: OrgAgendaItem = OrgAgendaItem(
        title=test_event.summary,
        timestamps=[OrgDate(start, end)],
        properties=test_event.properties,
        description=test_event.description
    )

    create_event(runner, org_item)
    event = assert_event_created('one', org_item)

    org_item.timestamps = [OrgDate(start_new, end_new)]
    org_item.properties['UID'] = event.uid
    edit_event('one', org_item)
    assert_event_edited(runner, 'one', org_item)


def test_calendar_edit_item_all_day(get_cli_runner: Callable):
    """
    After adding a new event, its addendees are added. When running khal
    list, the attendees should be visible.
    """
    test_event: Munch = munchify(_TEST_EVENT)  # type: ignore
    runner: CliRunner = get_cli_runner()
    start: datetime | date = datetime.date(datetime.today())
    end: datetime | date = start

    org_item: OrgAgendaItem = OrgAgendaItem(
        title=test_event.summary,
        timestamps=[OrgDate(start, end)],
        properties=test_event.properties,
        description=test_event.description
    )

    create_event(runner, org_item)
    event: Event = assert_event_created('one', org_item)
    org_item.properties['UID'] = event.uid
    edit_event('one', org_item)
    assert_event_edited(runner, 'one', org_item)


def test_calendar_edit_item_recurring(get_cli_runner: Callable):
    """
    After adding a new event, its addendees are added. When running khal
    list, the attendees should be visible.
    """
    days = 7
    test_event: Munch = munchify(_TEST_EVENT)  # type: ignore
    runner: CliRunner = get_cli_runner(days=7)

    start: datetime = datetime.now()
    end: datetime = datetime.now() + timedelta(hours=1)
    until = datetime.now() + timedelta(days=days)

    start = start.replace(second=0, microsecond=0)
    end = end.replace(second=0, microsecond=0)
    until = until.replace(second=0, microsecond=0)

    org_item: OrgAgendaItem = OrgAgendaItem(
        title=test_event.summary,
        timestamps=[OrgDate(start, end)],
        properties=test_event.properties,
        description=test_event.description
    )

    create_event(runner, org_item, repeat='daily', until=until)
    event: Event = assert_event_created('one', org_item, recurring=True)

    org_item.properties['UID'] = event.uid
    edit_event('one', org_item)
    assert_event_edited(runner, 'one', org_item, count=days)
