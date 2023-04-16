import logging
from collections import OrderedDict
from os.path import exists, join
from typing import Callable, Generator, Union

from khal.cli import build_collection
from khal.khalendar import CalendarCollection
from khal.settings.settings import (
    ConfigObj,
    find_configuration_file,
    get_config,
)

from paths import org_format, static_dir
from src.helpers import subprocess_callback
from src.org_items import NvimOrgDate, OrgAgendaItem


def get_calendar_collection(name: str) -> CalendarCollection:
    """
    Return the calendar collection for a specific calendar `name`.

    Args:
        name: name of the calendar

    Returns
    -------
        calendar collection
    """
    path_config: str | None = find_configuration_file()
    config: ConfigObj = get_config(path_config)
    return build_collection(config, name)


class Calendar:
    """
    Represents a Khal calendar.

    Attributes
    ----------
        name: calendar name
        config: Khal config
        list: export command (khal list)
        new_item: new command (khal new)
    """

    def __init__(self, name: str):
        """
        Init.

        Args:
        ----
            name: name of the khal calendar
        """
        path_config: Union[str, None] = find_configuration_file()
        list_format: str = self.get_list_format()

        new_item_args: list = ['khal', 'new']
        list_args: list = ['khal', 'list', '--format', list_format]

        self.name: str = name
        self.config: dict = get_config(path_config)
        self.new_item: Callable = subprocess_callback(new_item_args)
        self.list_command: Callable = subprocess_callback(list_args)

    @property
    def date_format(self) -> str:
        """
        longdatetimeformat.

        Returns
        -------

        """
        return self.config['locale']['longdateformat']

    @property
    def datetime_format(self) -> str:
        """
        longdatetimeformat.

        Returns
        -------

        """
        return self.config['locale']['longdatetimeformat']

    def get_list_format(self) -> str:
        """
        The format of the org item is returned.

        It is defined in *.txt file that exists in the config directory of the
        user as `org_format`. If it does nog exist, the `default_org_format` is
        used.

        Returns
        -------
            org format that is feeded to the `khal list --format` command.

        """
        default_org_format: str = join(static_dir, 'org_format.txt')
        path: str = org_format if exists(org_format) else default_org_format
        with open(path) as file_:
            return file_.read()


class KhalArgsError(Exception):
    """Raised for an error in Args."""


class KhalArgs(OrderedDict):

    REPEAT_ORG_TO_KHAL: dict = {
        '+1d': 'daily',
        '+1w': 'weekly',
        '+1m': 'monthly',
        '+1y': 'yearly'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        path_config: str | None = find_configuration_file()
        config: dict = get_config(path_config)
        self.date_format: str = config['locale']['longdateformat']
        self.datetime_format: str = config['locale']['longdatetimeformat']

    def as_list(self) -> list:
        """
        Return the OrderedDict as a list.

        The list is split base on white spaces. Strings surrouded by \"..\" are
        ignored for now.

        Returns
        -------
            an OrderedDict represented as a list.

        """
        generator: Generator = ((x, self[x]) for x in self.optional if self[x])
        optional: list = [x for key_value in generator for x in key_value]
        positional: list = [self[x] for x in self.positional if self[x]]
        return optional + positional

    @property
    def optional(self) -> dict:
        """
        Return only the optional args of Args.

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
        """
        Returns only the positional args of Args.

        Returns
        -------
            positional arguments.

        """
        def condition(key):
            return not self._is_option(key)

        return self._filter(condition)


class KhalArgsNew(KhalArgs):

    def load_from_org(self, item: OrgAgendaItem) -> 'KhalArgsNew':
        """
        For convenience: directly load Args from OrgAgendaItem.

        Load the command line arguments for khal into Args (which is an
        OrderedDict) directly from an OrgAgendaItem.

        Args:
            item: an OrgAgendaItem object.
            datetime_format: optionally, a timestamp format can be provided.

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

            if time_stamp.has_time():
                format: str = self.datetime_format
            else:
                format: str = self.date_format

            return self._load_from_org(time_stamp, item, format)

    def _load_from_org(self,
                       time_stamp: NvimOrgDate,
                       item: OrgAgendaItem,
                       format: str) -> 'KhalArgsNew':

        key_vs_value: tuple = (
            ('start', time_stamp.start.strftime(format)),
            ('end', self._get_end(time_stamp, format)),
            ('summary', item.heading),
            ('description', f':: {item.body}'),
            ('--location', item.properties.get('LOCATION', '')),
            ('--url', item.properties.get('URL', '')),
            ('--repeat', self._get_repeat(time_stamp))
        )

        for key, value in key_vs_value:
            if value:
                self[key] = value

        return self

    def _get_end(self, time_stamp: NvimOrgDate, format: str) -> str:
        """
        Returns the start time if no end time exists.

        Args:
            time_stamp: the end time
            format: format

        Returns
        -------
            timestamp as a str
        """
        try:
            return time_stamp.end.strftime(format)
        except AttributeError:
            logging.debug('End timestamp cannot be formatted.')
            return time_stamp.start.strftime(format)

    def _get_repeat(self, time_stamp: NvimOrgDate) -> str:
        try:
            key: str = ''.join([str(x) for x in time_stamp._repeater])
            return self.REPEAT_ORG_TO_KHAL[key]
        except KeyError as error:
            message: str = f'The repeat value of: {key} is not supported.'
            raise KhalArgsError(message) from error
        except TypeError:  # no repeater found
            return ''
