from datetime import datetime, timedelta
from test.helpers import get_test_config, khal_runner
from test.static.agenda_items import MaximalValid, Recurring
from typing import Callable
from unittest import TestCase
from unittest.mock import patch

import pytest
from click.testing import CliRunner
from khal.cli import main_khal

from src.khal_items import Calendar, KhalArgs, edit_attendees
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
    def test_timestamp_format(self, _):
        """The `timestamp_format` must coincide. """
        self.assertEqual(self.calendar.timestamp_format, '%Y-%m-%d %a %H:%M')


class TestArgs(Mixin, TestCase):

    def test_load_from_org(self):
        """
        When loaded from the org file maximal_valid.org, the resulting cli
        args must be the same as: MaximalValid.command_line_args
        .
        """
        actual: KhalArgs = KhalArgs()
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
        actual: KhalArgs = KhalArgs()
        actual.load_from_org(agenda_item)
        expected: dict = Recurring.command_line_args
        self.assertEqual(actual, expected)

    def test_optional(self):
        """ When adding an option, it can be retrieved using Args.optional. """
        key = '--url'
        value: str = 'www.test.com'
        args: KhalArgs = KhalArgs()
        args[key] = value
        self.assertEqual(value, args.optional[key])

    def test_positional(self):
        """
        When adding an positional arg, it can be retrieved using
        Args.optional.
        """
        key = 'foo'
        value: str = 'bar'
        args: KhalArgs = KhalArgs()
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
        args: KhalArgs = KhalArgs()
        args['--url'] = 'www.test.com'
        args['start'] = datetime(2023, 1, 1).strftime(FORMAT)

        expected: list = [
            '--url',
            'www.test.com',
            '2023-01-01',
            'Sun',
            '00:00']

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


def test_empty_calendar(get_cli_runner):
    runner = get_cli_runner()
    result = runner.invoke(main_khal, ['list'])
    assert result.output == ''
    assert not result.exception


def test_add_attendee(get_cli_runner: Callable):
    """
    After adding a new event, its addendees are added. When running khal
    list, the attendees should be visible.
    """
    runner: CliRunner = get_cli_runner()
    format: str = '%d.%m.%Y %H:%M'
    start: datetime = datetime.now()
    end: datetime = datetime.now() + timedelta(hours=1)
    start = start.replace(second=0, microsecond=0)
    end = end.replace(second=0, microsecond=0)
    attendees: list = ['test@test.com']

    summary: str = 'Summary'
    new_cmd: list = [
        'new',
        start.strftime(format),
        end.strftime(format),
        summary,
        '::',
        'Description'
    ]
    list_cmd: str = 'list --format {attendees}'

    runner.invoke(main_khal, new_cmd)
    events: list = edit_attendees('one', attendees, summary, start, end)
    result = runner.invoke(main_khal, list_cmd.split(' '))

    assert len(events) == 1
    assert events[0].attendees == attendees[0]
    assert attendees[0] in result.output
