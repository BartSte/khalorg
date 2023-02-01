import logging
from datetime import datetime
from test.helpers import get_test_config
from test.static.agenda_items import MaximalValid
from unittest import TestCase
from unittest.mock import patch

from src.khal_items import Args, Calendar
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
        """ When loaded from the org file maximal_valid.org, the resulting cli
        args must be the same as: MaximalValid.command_line_args
        .
        """
        actual: Args = Args()
        actual.load_from_org(self.agenda_item)
        expected: dict = MaximalValid.command_line_args
        self.assertEqual(actual, expected)

    def test_optional(self):
        """ When adding an option, it can be retrieved using Args.optional. """
        key = '--url'
        value: str = 'www.test.com'
        args: Args = Args()
        args[key] = value
        self.assertEqual(value, args.optional[key])

    def test_positional(self):
        """ When adding an positional arg, it can be retrieved using
        Args.optional. 
        """
        key = 'foo'
        value: str = 'bar'
        args: Args = Args()
        args[key] = value
        self.assertEqual(value, args.positional[key])

    def test_as_list(self):
        """ Args.as_list contatinates all Args in a list. The dictionary key of
        an option is prepended before its value. Of the positional args, only
        its value is retained (obviously). Later, all arguments are split based
        on a whitespace. Statements surrounded by quotes are not (yet)
        supported."""
        args: Args = Args()
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
