from subprocess import check_output
from typing import Callable, Union

from khal.settings.settings import find_configuration_file, get_config

from src.org_items import OrgAgendaItem


class Calendar:

    def __init__(self, name):
        path_config: Union[str, None] = find_configuration_file()
        self.config: dict = get_config(path_config)
        self.name: str = name

        self.new_item: Callable = SubProcessWithParser(
            cmd='khal new',
            parser=new_item_parser,
            args=[f'--calendar {self.name}']
        )

    @property
    def long_datetime_format(self) -> str:
        """TODO.

        Returns
        -------

        """
        return self.config['locale']['longdatetimeformat']


class SubProcess:

    def __call__(self, args: list) -> str:
        stdout: bytes = check_output(args)
        return stdout.decode()


class NewItem(SubProcess):

    def __init__(self, )

    def from_org_agenda_item(self, item: OrgAgendaItem) -> str:
        positional: tuple = (item.time_stamps.pop(), '')
        optional: tuple = (
            ('--location', item.properties['location']),
            ('--until', ''),
            ('--format', ''),
            ('--alarms', ''),
            ('--url' item.properties['URL']))

        args: list = []
        return super().__call__(args)

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
