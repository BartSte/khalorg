from datetime import date, datetime, timedelta
from dateutil.rrule import rrulestr
from khal.icalendar import rrulefstr

from test.helpers import (
    compare_without_white_space,
    khal_runner,
    read_org_test_file,
)
from typing import Callable
from unittest import TestCase

import pytest
from click.testing import CliRunner
from khal.cli import main_khal

from src.post_processors import (
    ListPostProcessor,
    convert_repeat_pattern,
    edit_attendees,
)


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
    description: str = "Hello,\n\n Text.\n\nBye"

    summary: str = 'Summary'
    new_cmd: list = [
        'new',
        start.strftime(format),
        end.strftime(format),
        summary,
        '::',
        description
    ]
    list_cmd: str = 'list --format {attendees}'

    runner.invoke(main_khal, new_cmd)
    edit_attendees('one', attendees, summary, start, end)
    result = runner.invoke(main_khal, list_cmd.split(' '))

    assert attendees[0] in result.output, result.output


def test_add_attendee_all_day_event(get_cli_runner: Callable):
    """
    After adding a new event, its addendees are added. When running khal
    list, the attendees should be visible.
    """
    runner: CliRunner = get_cli_runner()
    format: str = '%d.%m.%Y'
    start: datetime | date = datetime.date(datetime.today())
    end: datetime | date = start
    attendees: list = ['test@test.com']
    description: str = "Hello,\n\n Text.\n\nBye"
    summary: str = 'Summary'

    new_cmd: list = [
        'new',
        start.strftime(format),
        end.strftime(format),
        summary,
        '::',
        description
    ]
    list_cmd: str = 'list --format {attendees}'

    runner.invoke(main_khal, new_cmd)
    edit_attendees('one', attendees, summary, start, end)
    result = runner.invoke(main_khal, list_cmd.split(' '))

    assert attendees[0] in result.output


def test_add_attendee_recurring_event(get_cli_runner: Callable):
    """
    After adding a new event, its addendees are added. When running khal
    list, the attendees should be visible.
    """
    days: int = 7
    runner: CliRunner = get_cli_runner(days=days)
    format: str = '%d.%m.%Y %H:%M'
    start: datetime = datetime.now()
    end: datetime = datetime.now() + timedelta(hours=1)
    start = start.replace(second=0, microsecond=0)
    end = end.replace(second=0, microsecond=0)
    attendees: list = ['test@test.com']
    description: str = "Hello,\n\n Text.\n\nBye"
    summary: str = 'Summary'

    new_cmd: list = [
        'new',
        '--repeat', 'daily',
        start.strftime(format),
        end.strftime(format),
        summary,
        '::',
        description
    ]
    list_cmd: str = 'list --format {attendees}'

    runner.invoke(main_khal, new_cmd)
    edit_attendees('one', attendees, summary, start, end)
    result = runner.invoke(main_khal, list_cmd.split(' '))

    assert result.output.count(attendees[0]) == days


class TestConvertRepeatPattern(TestCase):
    """ Test converting the ical repeat pattern to the org repeat pattern. """

    def test(self):
        """
        The {repeat-pattern} format of khal prints the ical description
        of the repeat pattern of the event. This repeat pattern is converted to
        an org repeat pattern by the convert_repeat_pattern function, which is
        tested in this test.
        """
        org_vs_ics: tuple = (
            ('recurring.org', 'repeat_pattern_weekly.org'),
            ('recurring_monthly.org', 'repeat_pattern_monthly.org'),
            ('recurring_allday_weekly.org', 'repeat_pattern_allday_weekly.org'),
            ('recurring.org', 'repeat_pattern_weekly_no_end.org'),
            ('recurring.org', 'repeat_pattern_weekly_1TH.org'),
            ('maximal_valid.org', 'repeat_pattern_not_supported.org'),
        )
        for org, ics in org_vs_ics:
            item: str = read_org_test_file(ics)
            actual: str = convert_repeat_pattern(item)
            expected: str = read_org_test_file(org)
            message: str = f'Test file: {ics}\n\n\n{item}'
            self.assertEqual(expected, actual, msg=message)

class TestListPostProcessor(TestCase):
    """ Test if duplicated items are removed. """

    def test_duplicates(self):
        """ A duplicate is present maximal_valid.org is duplicated. """
        post_processor: ListPostProcessor
        duplicate: str = read_org_test_file("duplicate.org")
        post_processor = ListPostProcessor.from_str(duplicate)

        expected: str = read_org_test_file("maximal_valid.org")
        actual: str = post_processor.remove_duplicates()

        self.assertTrue(compare_without_white_space(expected, actual))

    def test_no_duplicates(self):
        """ No duplicate is present so no changed are expected. """
        post_processor: ListPostProcessor
        expected: str = read_org_test_file("no_duplicates.org")

        post_processor = ListPostProcessor.from_str(expected)
        actual: str = post_processor.remove_duplicates()

        self.assertTrue(compare_without_white_space(expected, actual))

    def test_duplicate_recurring(self):
        """
        Items with a repeat pattern can be considered a duplicates if they
        have the same UID while having different timestamps.
        """
        post_processor: ListPostProcessor
        duplicate: str = read_org_test_file("duplicate_recurring.org")

        post_processor = ListPostProcessor.from_str(duplicate)
        actual: str = post_processor.remove_duplicates()
        expected: str = read_org_test_file("recurring.org")

        message: str = f'\nActual: {actual}\n Expected: {expected}'
        equal: bool = compare_without_white_space(actual, expected)
        self.assertTrue(equal, msg=message)
