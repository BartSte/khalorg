import logging
from os.path import join, exists
from paths import org_format, static_dir
from collections import OrderedDict
from typing import Callable, Union

from khal.settings.settings import find_configuration_file, get_config

from src.helpers import get_module_path, subprocess_callback
from src.org_items import NvimOrgDate, OrgAgendaItem


class KhalArgsError(Exception):
    """Raised for an error in Args."""


class Calendar:

    """Represents a Khal calendar.

    Attributes: 
        name: calendar name
        config: Khal config
        export: export command (khal list)
        new_item: new command (khal new)
    """
    def __init__(self, name: str):
        """Init.

        Args:
            name: name of the khal calendar
        """
        path_config: Union[str, None] = find_configuration_file()
        export_format: str = self.get_export_format()

        new_item_args: list = ['khal', 'new']
        export_args: list = ['khal', 'list', '--format', export_format]

        self.name: str = name
        self.config: dict = get_config(path_config)
        self.export: Callable = subprocess_callback(export_args)
        self.new_item: Callable = subprocess_callback(new_item_args)

    @property
    def timestamp_format(self) -> str:
        """longdatetimeformat.

        Returns
        -------

        """
        return self.config['locale']['longdatetimeformat']

    def get_export_format(self) -> str:
        """The format of the org item is returned.

        It is defined in *.txt file that exists in the config directory of the
        user as `org_format`. If it does nog exist, the `default_org_format` is
        used.

        Returns:
            org format that is feeded to the `khal list --format` command.
            
        """
        default_org_format: str = join(static_dir, 'org_format.txt')
        path: str = org_format if exists(org_format) else default_org_format
        with open(path) as file_:
            return file_.read()


class KhalArgs(OrderedDict):

    def load_from_org(
            self,
            item: OrgAgendaItem,
            timestamp_format: str = '%Y-%m-%d %a %H:%M') -> 'KhalArgs':
        """
        For convenience: directly load Args from OrgAgendaItem.

        Load the command line arguments for khal into Args (which is an
        OrderedDict) directly from an OrgAgendaItem.

        Args:
            item: an OrgAgendaItem object.
            timestamp_format: optionally, a timestamp format can be provided.

        Returns
        -------
            itself

        """
        # For now, only 1 timestamp is supported
        try:
            time_stamp: NvimOrgDate = item.time_stamps[0]
        except IndexError as error:
            raise KhalArgsError('Timestamp missing in agenda item') from error
        else:
            return self._load_from_org(time_stamp, item, timestamp_format)

    def _load_from_org(self,
                       time_stamp: NvimOrgDate,
                       item: OrgAgendaItem,
                       timestamp_format: str) -> 'KhalArgs':

        key_vs_value: tuple = (
            ('start', time_stamp.start.strftime(timestamp_format)),
            ('end', self._get_end(time_stamp, timestamp_format)),
            ('summary', item.heading),
            ('description', f':: {item.body}'),
            ('--location', item.properties.get('LOCATION', '')),
            ('--url', item.properties.get('URL', ''))
        )

        for key, value in key_vs_value:
            self[key] = value

        return self

    def _get_end(self,
                 time_stamp: NvimOrgDate,
                 timestamp_format: str = '%Y-%m-%d %a %H:%M') -> str:
        try:
            return time_stamp.end.strftime(timestamp_format)
        except AttributeError:
            logging.debug('End timestamp cannot be formatted.')
            return ''

    def as_list(self) -> list:
        """
        Return the OrderedDict as a list.

        The list is split base on white spaces. Strings surrouded by \"..\" are
        ignored for now.

        Returns
        -------
            an OrderedDict represented as a list.

        """
        optional: list = [f'{x} {self[x]}' for x in self.optional if self[x]]
        positional: list = [self[x] for x in self.positional if self[x]]
        as_str: str = ' '.join(optional + positional)
        return as_str.split(' ')

    @property
    def optional(self) -> dict:
        """Return only the optional args of Args.

        Returns
        -------
            optional arguments.

        """
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
        """Returns only the positional args of Args.

        Returns
        -------
            positional arguments.

        """
        def condition(key):
            return not self._is_option(key)

        return self._filter(condition)
