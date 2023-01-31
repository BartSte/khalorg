import logging
from datetime import datetime
from test.helpers import get_test_config
from test.static.agenda_items import MaximalValid
from unittest import TestCase
from unittest.mock import patch

from src.khal_items import Args, Calendar
from src.org_items import OrgAgendaItem


class Mixin:

    def setUp(self) -> None:
        logging.basicConfig(level=logging.DEBUG)
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
        actual: Args = Args()
        actual.load_from_org(self.agenda_item)
        expected: dict = MaximalValid.command_line_args
        self.assertEqual(actual, expected)

    def test_optional(self):
        key = '--url'
        value: str = 'www.test.com'
        args: Args = Args()
        args[key] = value
        self.assertEqual(value, args.optional[key])

    def test_positional(self):
        key = 'foo'
        value: str = 'bar'
        args: Args = Args()
        args[key] = value
        self.assertEqual(value, args.positional[key])

    def test_as_list(self):
        args: Args = Args()
        args['--url'] = 'www.test.com'
        args['start'] = str(datetime(2023, 1, 1))

        expected: list = ['--url www.test.com', '2023-01-01 00:00:00']
        actual: list = args.as_list()
        self.assertEqual(actual, expected)
