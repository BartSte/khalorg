from typing import Callable, Union

from khal.settings.settings import find_configuration_file, get_config
from src.helpers import SubProcessWithParser

from src.org_items import OrgAgendaItem


class Calendar:

    def __init__(self, name):
        path_config: Union[str, None] = find_configuration_file()
        self.config: dict = get_config(path_config)
        self.name: str = name

        self.new_item: Callable = SubProcessWithParser('khal new', org_to_khal_new)
        self.edit_item: Callable = SubProcessWithParser('khal edit', from_org)
        self.get_item: Callable = SubProcessWithParser('khal format', from_org)

    @property
    def long_datetime_format(self) -> str:
        """TODO.

        Returns
        -------

        """
        return self.config['locale']['longdatetimeformat']



def org_to_khal_new(agenda_item: OrgAgendaItem) -> list:
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
