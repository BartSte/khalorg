import os
from datetime import date, datetime, timedelta
from os.path import join

import pytest
from test import static
from typing import Any, Callable

from click.testing import CliRunner, Result
from khal.cli import main_khal
from khal.controllers import Event

from src.helpers import get_module_path
from src.khal_items import (
    Calendar,
    CalendarProperties,
    EditArgs,
    NewArgs,
)
from src.org_items import OrgAgendaItem


def get_test_config() -> str:
    path_static: str = get_module_path(static)
    return join(path_static, 'test_config_khal')


def read_org_test_file(org_file: str) -> str:
    """
    Reads an `org_file` and converts it into an `OrgNode` object. The
    directory is fixed and set to: /test/static/agenda_items.

    Args:
    ----
        org_file (str): path to an org file.

    Returns
    -------
        str: org file is converted to a string.

    """
    path: str = join(get_module_path(static), "agenda_items", org_file)
    with open(path) as org:
        return org.read()


def compare_without_white_space(a, b) -> bool:
    return compare_with_exclude(a, b, ('', '\n', '\t'))


def compare_with_exclude(a: str, b: str, excludes: tuple = tuple()) -> bool:
    return _filter(a, excludes) == _filter(b, excludes)


def _filter(text: str, excludes: tuple) -> list:
    return [x for x in text.splitlines() if x not in excludes]


class CustomCliRunner(CliRunner):
    def __init__(
            self,
            config_file,
            db=None,
            calendars=None,
            xdg_data_home=None,
            xdg_config_home=None,
            tmpdir=None,
            **kwargs):
        self.config_file = config_file
        self.db = db
        self.calendars = calendars
        self.xdg_data_home = xdg_data_home
        self.xdg_config_home = xdg_config_home
        self.tmpdir = tmpdir

        super().__init__(**kwargs)

    def invoke(self, cli, args=None, *a, **kw):
        args = ['-c', str(self.config_file)] + (args or [])
        return super().invoke(cli, args, *a, **kw)


def khal_runner(tmpdir, monkeypatch) -> Callable:
    """
    This test was copied from khal -> tests/cli_test.py. You can find it
    here: khal/test/cli_test.py.

    In contrast to the other test, this test relies on `pytest` instead of
    unittest. Since `pytest` is also compatible with `unittest` code, this will
    be no problem.

    The runner adds three calendar to khal: one, two, and three. Calendar "one"
    is the default calendar.

    Args:
    ----
        tmpdir: build-in pytest fixture for temporary directories
        monkeypatch: build-in pytest fixture for patching.

    Returns
    -------
        a test runner function

    """
    db = tmpdir.join('khal.db')
    calendar = tmpdir.mkdir('calendar')
    calendar2 = tmpdir.mkdir('calendar2')
    calendar3 = tmpdir.mkdir('calendar3')
    config_template: str = get_config_template()

    xdg_data_home = tmpdir.join('vdirs')
    xdg_config_home = tmpdir.join('.config')
    config_file = xdg_config_home.join('khal').join('config')

    monkeypatch.setattr('vdirsyncer.cli.config.load_config', lambda: Config())
    monkeypatch.setattr('xdg.BaseDirectory.xdg_data_home', str(xdg_data_home))
    monkeypatch.setattr('xdg.BaseDirectory.xdg_config_home', str(xdg_config_home))  # noqa
    monkeypatch.setattr('xdg.BaseDirectory.xdg_config_dirs', [str(xdg_config_home)])  # noqa

    def inner(print_new=False, default_calendar=True, days=2, **kwargs):
        if default_calendar:
            default_calendar = 'default_calendar = one'
        else:
            default_calendar = ''
        if not os.path.exists(str(xdg_config_home.join('khal'))):
            os.makedirs(str(xdg_config_home.join('khal')))
        config_file.write(
            config_template.format(
                delta=str(days) + 'd',
                calpath=str(calendar),
                calpath2=str(calendar2),
                calpath3=str(calendar3),
                default_calendar=default_calendar,
                print_new=print_new,
                dbpath=str(db),
                **kwargs))
        runner = CustomCliRunner(
            config_file=config_file, db=db, calendars={"one": calendar},
            xdg_data_home=xdg_data_home, xdg_config_home=xdg_config_home,
            tmpdir=tmpdir,
        )
        return runner
    return inner


def get_config_template() -> str:
    """
    Returns a config as a str with fields that can be formatted by
    str.format.

    Returns
    -------
        a config template

    """
    path_static: str = get_module_path(static)
    path_config: str = join(path_static, 'config_template.txt')
    with open(path_config) as file_:
        return file_.read()


class Config():
    """
    Copied from khal.cli_test.

    helper class for mocking vdirsyncer's config objects.
    """

    storages = {
        'home_calendar_local': {
            'type': 'filesystem',
            'instance_name': 'home_calendar_local',
            'path': '~/.local/share/calendars/home/',
            'fileext': '.ics',
        },
        'events_local': {
            'type': 'filesystem',
            'instance_name': 'events_local',
            'path': '~/.local/share/calendars/events/',
            'fileext': '.ics',
        },
        'home_calendar_remote': {
            'type': 'caldav',
            'url': 'https://some.url/caldav',
            'username': 'foo',
            'password.fetch': ['command', 'get_secret'],
            'instance_name': 'home_calendar_remote',
        },
        'home_contacts_remote': {
            'type': 'carddav',
            'url': 'https://another.url/caldav',
            'username': 'bar',
            'password.fetch': ['command', 'get_secret'],
            'instance_name': 'home_contacts_remote',
        },
        'home_contacts_local': {
            'type': 'filesystem',
            'instance_name': 'home_contacts_local',
            'path': '~/.local/share/contacts/',
            'fileext': '.vcf',
        },
        'events_remote': {
            'type': 'http',
            'instance_name': 'events_remote',
            'url': 'http://list.of/events/',
        },
    }


def create_event(
        runner: Any,
        org_item: OrgAgendaItem,
        repeat: str = '',
        until: datetime | date | None = None):
    """
    Create a new event.

    Args:
    ----
        runner: click runner
        calendar_name: name of calendar
        event_props: event values
        start: start date
        end: end date
        repeat: set to daily, weekly, monhtly, or yearly
    """
    args: NewArgs = NewArgs()
    args['--repeat'] = repeat

    if isinstance(until, datetime):
        args['--until'] = until.strftime(args.datetime_format)
    elif isinstance(until, date):
        args['--until'] = until.strftime(args.date_format)

    args.load_from_org(org_item)

    new_cmd: list = ['new'] + args.as_list()
    stdout: Result = runner.invoke(main_khal, new_cmd)
    assert stdout.exit_code == 0, stdout.output


def assert_event_created(
        calendar_name: str,
        org_item: OrgAgendaItem,
        recurring: bool = False) -> list[Event]:
    """
    Test if an event exists based on its summary and timestamp.

    Args:
    ----
      calendar_name: name of calendar
      event_props: event values
      start: start date
      end: start date
    """
    calendar: Calendar = Calendar(calendar_name)
    args: EditArgs = EditArgs()
    args.load_from_org(org_item)
    events: list[Event] = calendar.get_events_no_uid(args['summary'],
                                                     args['start'],
                                                     args['end'])
    assert len(events) >= 1, f'Number of events was {len(events)}'

    assert events[0].uid, 'UID is empty'
    assert recurring == events[0].recurring, f'recurring is {events[0].recurring}'

    return events


def edit_event(calendar_name: str, org_item: OrgAgendaItem):
    """
    Test if an event is edited properly. It is found based on its summary
    and timestamp.

    Args:
    ----
        runner: click runner
        calendar_name: name of calendar
        summary:
        start: start date
        end: end date
    """
    args: EditArgs = EditArgs()
    args.load_from_org(org_item)
    calendar: Calendar = Calendar(calendar_name)
    calendar.edit(CalendarProperties(**args))


def assert_event_edited(runner: Any,
                        calendar_name: str,
                        org_item: OrgAgendaItem,
                        count: int = 1):
    """
    Asserts whether the event, defined by event_props, start, and end
    exitst.

    Args:
    ----
        runner: click runner
        calendar_name: name of calendar
        org_item: org agenda item
    """
    calendar: Calendar = Calendar(calendar_name)
    events: list[Event] = calendar.get_events(org_item.properties['UID'])
    assert len(events) == count, f'Number of events is {len(events)}'

    list_fields: list = [
        'start-long',
        'end-long',
        'attendees',
        'categories',
        'location',
        'url']

    list_cmd: list = [
        "list",
        "--format", ' '.join([f'{{{x}}}' for x in list_fields])
    ]

    result = runner.invoke(main_khal, list_cmd)
    expected: list[str] = _get_expected_list_command(calendar, org_item,
                                                     list_fields, count)
    assert all(x in result.output for x in expected)


def _get_expected_list_command(
        calendar: Calendar,
        org_item: OrgAgendaItem,
        list_fields: list[str],
        count: int = 1,
        delta: timedelta = timedelta(0)) -> list[str]:
    """Returns the expected list command for the "assert_event_edited"
    function.

    Args:
        calendar: khal calendar
        org_item: the org_item used for editing
        list_fields: the fields used for the --format command
        count: number of repeats
        delta: timedelta between recurring events

    Returns
    -------
       list with the expected fields.
    """
    start: datetime | date = org_item.first_timestamp.start
    end: datetime | date = org_item.first_timestamp.end
    if org_item.first_timestamp.has_time():
        format: str = calendar.datetime_format
    else:
        format: str = calendar.date_format

    expected: list = []
    props: str = ' '.join([org_item.properties[x.upper()]
                           for x in list_fields[2:]])
    for _ in range(0, count - 1):
        value: str = f'{start.strftime(format)} {end.strftime(format)} '
        expected.append(value + props)
        start = start + delta
        end = end + delta

    return expected

