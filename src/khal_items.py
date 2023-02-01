from typing import Callable, Union

from khal.settings.settings import find_configuration_file, get_config

from src.helpers import subprocess_callback
from src.org_items import NvimOrgDate, OrgAgendaItem


class Calendar:

    def __init__(self, name):
        """

        Args:
        ----
            name ():
        """
        path_config: Union[str, None] = find_configuration_file()

        self.config: dict = get_config(path_config)
        self.name: str = name
        self.new_item: Callable = subprocess_callback(['khal', 'new'])

    @property
    def timestamp_format(self) -> str:
        """longdatetimeformat.

        Returns
        -------

        """
        return self.config['locale']['longdatetimeformat']


class Args(dict):

    def load_from_org(
            self,
            item: OrgAgendaItem,
            timestamp_format: str = '%Y-%m-%d %a %H:%M') -> 'Args':

        # For now, only 1 timestamp is supported
        time_stamp: NvimOrgDate = item.time_stamps[0]

        end: str = self._get_end(time_stamp, timestamp_format)
        body: str = f':: {item.body}'

        # TODO what if some items if OrgAgendaItem dont exist?
        key_vs_value: tuple = (
            ('start', time_stamp.start.strftime(timestamp_format)),
            ('end', end),
            ('summary', item.heading),
            ('description', body),
            ('--location', item.properties['LOCATION']),
            ('--url', item.properties['URL'])
        )

        for key, value in key_vs_value:
            self[key] = value

        return self

    def _get_end(
            self, time_stamp: NvimOrgDate,
            timestamp_format: str = '%Y-%m-%d %a %H:%M') -> str:
        if time_stamp.has_end:
            return time_stamp.end.strftime(timestamp_format)
        else:
            return ''

    def as_list(self) -> list:
        optional: list = [f'{x} {self[x]}' for x in self.optional if self[x]]
        positional: list = [self[x] for x in self.positional if self[x]]
        as_str: str = ' '.join(optional + positional)
        return as_str.split(' ')
        
    @property
    def optional(self) -> dict:
        return self._filter(self._is_option)

    def _filter(self, condition) -> dict:
        return {key: value for key, value in self.items() if condition(key)}

    @staticmethod
    def _is_option(key: str) -> bool:
        try:
            return key[0] == '-'
        except IndexError:
            return False

    @property
    def positional(self) -> dict:

        def condition(key):
            return not self._is_option(key)

        return self._filter(condition)
