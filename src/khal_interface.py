from subprocess import check_output
from typing import Callable, Union

from khal.settings.settings import find_configuration_file, get_config

from src.org_items import OrgAgendaItem


class Calendar:

    def __init__(self, name):
        path_config: Union[str, None] = find_configuration_file()
        self.config: dict = get_config(path_config)
        self.name: str = name

        self.new_item: Callable = Command('new', from_org)
        self.edit_item: Callable = Command('edit', from_org)
        self.get_item: Callable = Command('format', from_org)

    @property
    def long_datetime_format(self) -> str:
        """TODO.

        Returns
        -------

        """
        return self.config['locale']['longdatetimeformat']


class Command:

    BIN: str = 'khal'

    def __init__(
            self,
            first_arg: str,
            from_org: Callable = lambda: []) -> None:
        self.first_arg: str = first_arg
        self.from_org: Callable = from_org

    def __call__(self, args: tuple) -> str:
        stdout: bytes = check_output([self.BIN, self.first_arg, *args])
        return stdout.decode()


def from_org(agenda_item: OrgAgendaItem) -> list:
    return []

    # """
    # Usage: khal new [OPTIONS] [START [END | DELTA] [TIMEZONE] [SUMMARY]
    # [:: DESCRIPTION]].
    # """
    # options: tuple[tuple[str, str], ...] = (
    #     ('--calendar', self.name),
    #     ('--location', item.properties['location']),
    #     ('--categories', ''),
    #     ('--repeat', ''),
    #     ('--until', ''),
    #     ('--format', ),
    #     ('--alarms', ),
    #     ('--url' item.properties['URL'])
    # )
    # command: list = ['khal new']
    # optional: list = [f'{x} {y}' for x, y in options if y]
    # positional: list = [
    #     ''
    # ]

    # self._execute(command)

    # new_item_program: str = 'khal new'
    # new_item_args: tuple = (
    #     'start',
    #     'end',
    #     'delta',
    #     'timezone',
    #     'summary',
    #     'description')
    # new_item_options: tuple = (
    #     '--calendar',
    #     '--location',
    #     '--categories',
    #     '--repeat',
    #     '--until',
    #     '--format',
    #     '--alarms',
    #     '--url')
