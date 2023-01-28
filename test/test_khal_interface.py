import logging
from subprocess import CalledProcessError
from test.static.agenda_items import MaximalValid
from typing import Callable
from unittest import TestCase

from src.khal_interface import CalendarCommand, NewItem
from src.org_items import OrgAgendaItem


class TestCalendarCommand(TestCase):

    def setUp(self) -> None:
        logging.basicConfig(level=logging.DEBUG)
        args: list = MaximalValid.get_args()
        self.agenda_item: OrgAgendaItem = OrgAgendaItem(*args)
        return super().setUp()

    def test_call(self):
        khal: Callable = CalendarCommand('khal')
        try:
            khal(['--help'])
        except CalledProcessError as error:
            self.fail(error.stdout)

    def test_parse_positional(self):
        command: Callable = CalendarCommand()
        actual: dict = command.parse_positional(self.agenda_item)
        expected: dict = MaximalValid.khal_positional_args
        self.assertEqual(actual, expected)

    def test_parse_optional(self):
        calendar: str = 'Some_calendar'
        command: Callable = CalendarCommand(calendar=calendar)
        actual: dict = command.parse_optional(self.agenda_item)
        expected: dict = MaximalValid.khal_optional_args

        expected['-a'] = calendar
        expected['--calendar'] = calendar

        self.assertEqual(actual, expected)


class TestGetArgsKhalNew(TestCase):

    def test(self):
        positional: dict = MaximalValid.khal_positional_args
        optional: dict = MaximalValid.khal_optional_args
        optional['-a'] = 'Some_calendar'

        actual: list = NewItem.get_args(positional, optional)
        expected: list = MaximalValid.khal_new_args

        self.maxDiff = None
        self.assertEqual(actual, expected)
