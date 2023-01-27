from itertools import chain
from subprocess import check_output
from typing import Callable, Union

from khal.settings.settings import find_configuration_file, get_config

from src.org_items import NvimOrgDate, OrgAgendaItem


class Calendar:

    def __init__(self, name):
        path_config: Union[str, None] = find_configuration_file()
        self.config: dict = get_config(path_config)
        self.name: str = name

        self.new_item: Callable = CalendarCommand('khal new',
                                                  name,
                                                  self.timestamp_format)

    @property
    def timestamp_format(self) -> str:
        """longdatetimeformat.

        Returns
        -------

        """
        return self.config['locale']['longdatetimeformat']


class CalendarCommand:

    def __init__(
            self,
            bin: str,
            calendar_name: str,
            timestamp_format: str = '%Y-%m-%d %a %H:%M') -> None:

        self.bin: str = bin
        self.calendar_name: str = calendar_name
        self.timestamp_format: str = timestamp_format

    def __call__(self, args: list) -> str:
        stdout: bytes = check_output(args)
        return stdout.decode()

    def from_org_agenda_item(self, item: OrgAgendaItem) -> str:
        positional: tuple = self.parse_positional(item)
        optional: tuple = self.parse_optional(item)
        args: list = [f'{x} {y}' for x, y in chain(optional, positional)]
        return self(args)

    def parse_positional(self, item: OrgAgendaItem) -> tuple:
        # For now, only 1 timestamp is supported
        time_stamp: NvimOrgDate = item.time_stamps[0]
        start: str = time_stamp.start.strftime(self.timestamp_format)

        if time_stamp.has_end:
            end: str = time_stamp.end.strftime(self.timestamp_format)
        else:
            end = ""

        summary: str = item.heading
        description: str = item.body

        return start, end, summary, '::', description

    def parse_optional(self, item: OrgAgendaItem) -> tuple:
        return (
            ('--calendar', self.calendar_name),
            ('--location', item.properties['location']),
            ('--url', item.properties['URL']),
            ('--format', self.timestamp_format),
            ('--alarms', ''),
            ('--repeat', ''),
            ('--until', '')
        )

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
