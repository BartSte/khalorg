from datetime import date, datetime, timedelta
from test.helpers import khal_runner
from typing import Callable

import pytest
from click.testing import CliRunner
from khal.cli import main_khal

from src.hacks import edit_attendees


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
    events: list = edit_attendees('one', attendees, summary, start, end)
    result = runner.invoke(main_khal, list_cmd.split(' '))

    assert len(events) == 1
    assert events[0].attendees == attendees[0]
    assert attendees[0] in result.output

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
    events: list = edit_attendees('one', attendees, summary, start, end)
    result = runner.invoke(main_khal, list_cmd.split(' '))

    assert len(events) == 1
    assert events[0].attendees == attendees[0]
    assert attendees[0] in result.output
