import os
from os.path import join
from test import static
from typing import Callable

from click.testing import CliRunner

from src.helpers import get_module_path


def get_test_config() -> str:
    path_static: str = get_module_path(static)
    return join(path_static, 'test_config_khal')


def read_org_test_file(org_file: str) -> str:
    """
    Reads an `org_file` and converts it into an `OrgNode` object. The
    directory is fixed and set to: /test/static/agenda_items.

    Args:
        org_file (str): path to an org file.

    Returns
    -------
        str: org file is converted to a string.

    """
    path: str = join(get_module_path(static), "agenda_items", org_file)
    with open(path) as org:
        return org.read()


def compare_without_white_space(a, b) -> bool:
    return compare_with_exclude(a, b, ('',  '\n', '\t'))


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
    """Copied from khal.cli_test.

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
