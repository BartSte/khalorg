from tests.helpers import (
    get_test_config,
    khal_runner,
)
from tests.test_khal.helpers import Mixin
from typing import Callable
from unittest import TestCase
from unittest.mock import patch

import pytest
from khal.controllers import CalendarCollection

from khalorg.khal.calendar import get_calendar_collection



@pytest.fixture
def get_cli_runner(tmpdir, monkeypatch) -> Callable:
    return khal_runner(tmpdir, monkeypatch)


def test_get_calendar_collection(get_cli_runner):
    """Must be able to find a calendar collection."""
    get_cli_runner()
    collection: CalendarCollection = get_calendar_collection('one')
    assert isinstance(collection, CalendarCollection)


def test_get_calendar_collection_no_config(get_cli_runner):
    """
    Must be able to find a calendar collection. Even if no configuration
    file can be found.
    """
    from khalorg.khal import calendar
    calendar.find_configuration_file = lambda *_: None

    get_cli_runner()
    collection: CalendarCollection = get_calendar_collection('noneexisting')
    assert isinstance(collection, CalendarCollection)


class TestCalendar(Mixin, TestCase):

    module: str = 'khalorg.khal.calendar.find_configuration_file'

    @patch(module, return_value=get_test_config())
    def test_datetime_format(self, _):
        """The `datetime_format` must coincide. """
        self.assertEqual(self.calendar.datetime_format, '%Y-%m-%d %a %H:%M')
