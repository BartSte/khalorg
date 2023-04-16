from datetime import datetime
from test.helpers import get_test_config, khal_runner
from test.agenda_items import AllDay, MaximalValid, Recurring
from typing import Callable
from unittest import TestCase
from unittest.mock import patch

import pytest
from khal.khalendar import CalendarCollection

from src.khal_items import Calendar, NewArgs, get_calendar_collection
from src.org_items import OrgAgendaItem

FORMAT = '%Y-%m-%d %a %H:%M'


class Mixin:

    def setUp(self) -> None:
        args: list = MaximalValid.get_args()
        self.agenda_item: OrgAgendaItem = OrgAgendaItem(*args)
        self.calendar = Calendar('test_calendar')


class TestCalendar(Mixin, TestCase):

    @patch('src.khal_items.find_configuration_file',
           return_value=get_test_config())
    def test_datetime_format(self, _):
        """The `datetime_format` must coincide. """
        self.assertEqual(self.calendar.datetime_format, '%Y-%m-%d %a %H:%M')


class TestArgs(Mixin, TestCase):

    def test_load_from_org(self):
        """
        When loaded from the org file maximal_valid.org, the resulting cli
        args must be the same as: MaximalValid.command_line_args
        .
        """
        actual: NewArgs = NewArgs()
        actual.load_from_org(self.agenda_item)
        expected: dict = MaximalValid.command_line_args
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
        """ TODO """
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
