from test.helpers import (
    assert_event_created,
    get_org_item,
    khal_runner,
    read_org_test_file,
)
from typing import Callable, Generator

import pytest
from khal.cli import main_khal

from src.commands import new
from src.khal.calendar import Calendar
from src.khal.checker import EventChecker
from src.org.agenda_items import OrgAgendaItem


@pytest.fixture
def get_cli_runner(tmpdir, monkeypatch) -> Callable:
    return khal_runner(tmpdir, monkeypatch)


@pytest.fixture
def runner(get_cli_runner, monkeypatch) -> Generator:
    """
    Returns a test runnen that is created by CliRunner.

    The Calendar.new_item is monkeypatched to enable using the temporarly
    created calendar.

    Args:
    ----
        get_cli_runner: fixture
        monkeypatch: fixture

    Returns:
    -------
        test runner
    """
    runner = get_cli_runner()

    def khal_new(_, args: list) -> str:
        result = runner.invoke(main_khal, ['new'] + args)
        return result.output

    def khal_list(_, args: list):
        result = runner.invoke(main_khal, ['list', '-df', ''] + args)
        return result.output

    monkeypatch.setattr(Calendar, 'new_item', khal_new)
    monkeypatch.setattr(Calendar, 'list_command', khal_list)

    yield runner


def test_duplicate(runner, caplog):
    """When an item is duplicated, log a critical message."""
    org_item: OrgAgendaItem = get_org_item()
    new('one', org=str(org_item))
    assert_event_created('one', org_item)
    new('one', org=str(org_item))
    assert 'Agenda item already exists' in caplog.text


def test_event_in_past(runner, caplog):
    """When an item its timestamp is in the past, log a critical message."""
    new('one', org=read_org_test_file('past.org'))
    assert 'Agenda item date not in the future' in caplog.text


def test_new_max_weeks(runner, caplog):
    """
    An error message should be logged when exceeding the max number of
    weeks.
    """
    expected: OrgAgendaItem = get_org_item(repeater=('+', 53, 'w'))
    new('one', org=str(expected))
    assert EventChecker.MESSAGE_RRULE in caplog.text
