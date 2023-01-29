import logging
from datetime import datetime
from subprocess import CalledProcessError
from test.helpers import get_test_config
from test.static.agenda_items import MaximalValid
from typing import Callable
from unittest import TestCase
from unittest.mock import patch

from src import khal_interface
from src.khal_interface import Calendar, Command, CommandLineArgs
from src.org_items import OrgAgendaItem


def patch_check_output(args: list) -> bytes:
    return ' '.join(args).encode()


class Mixin:

    def setUp(self) -> None:
        logging.basicConfig(level=logging.DEBUG)
        args: list = MaximalValid.get_args()
        self.agenda_item: OrgAgendaItem = OrgAgendaItem(*args)
        self.calendar = Calendar('test_calendar')


class TestCalendar(Mixin, TestCase):

    @patch('src.khal_interface.find_configuration_file',
           return_value=get_test_config())
    def test_timestamp_format(self, _):
        """The `timestamp_format` must coincide. """
        self.assertEqual(self.calendar.timestamp_format, '%Y-%m-%d %a %H:%M')


class TestCalendarCommand(Mixin, TestCase):

    @patch.object(khal_interface, 'check_output', patch_check_output)
    def test_call(self):
        """ The __call__ method should run the `khal --help` command as a
        subprocess.
        """
        cmd: Callable = Command('foo')
        actual: str = cmd(['bar', '--help'])
        expected: str = 'foo bar --help'
        self.assertEqual(actual, expected)

    @patch.object(khal_interface, 'check_output', patch_check_output)
    def test_from_dict(self):
        cmd: Command = Command('khal new')
        kwargs: dict = CommandLineArgs()
        kwargs['start'] = str(datetime(2023, 1, 1))
        kwargs['--url'] = 'www.test.com'

        expected: str = 'khal new --url www.test.com 2023-01-01 00:00:00'
        actual: str = cmd.from_dict(kwargs)
        self.assertEqual(actual, expected)


class TestCommandLineArgs(Mixin, TestCase):

    def test(self):
        actual: CommandLineArgs = CommandLineArgs()
        actual.load_from_org(self.agenda_item)
        expected: dict = MaximalValid.command_line_args
        self.assertEqual(actual, expected)
