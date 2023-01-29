from itertools import chain
from subprocess import check_output
from typing import Union

from khal.settings.settings import find_configuration_file, get_config

from src.org_items import NvimOrgDate, OrgAgendaItem


class Calendar:

    """TODO.

    Attributes
    ----------
        config:
        name:
        new_item:
    """

    def __init__(self, name):
        """

        Args:
        ----
            name ():
        """
        path_config: Union[str, None] = find_configuration_file()

        self.config: dict = get_config(path_config)
        self.name: str = name
        self.new_item: Command = Command('khal new', name, self.timestamp_format)  # noqa

    @property
    def timestamp_format(self) -> str:
        """longdatetimeformat.

        Returns
        -------

        """
        return self.config['locale']['longdatetimeformat']


class Command:

    FORMAT: str = '%Y-%m-%d %a %H:%M'

    def __init__(
            self,
            bin: str,
            calendar: str = '',
            timestamp_format: str = FORMAT) -> None:

        self.bin: str = bin
        self.calendar: str = calendar
        self.timestamp_format: str = timestamp_format

    def __call__(self, args: list) -> str:
        """TODO.

        Args:
            args:

        Returns
        -------

        """
        stdout: bytes = check_output([self.bin, *args])
        return stdout.decode()

    def from_dict(self, kwargs: dict) -> str:
        """TODO.

        All non empty values of a dict will be used as cli arguments.

        TODO what defines the order?

        Args:
            positional:
            optional:

        Returns
        -------

        """
        positional: dict = CommandLineArgs.filter_positional(kwargs) 
        optional: dict = CommandLineArgs.filter_optional(kwargs)
        args: list = [f'{x} {kwargs[x]}' for x in optional if kwargs[x]]
        args += [kwargs[x] for x in positional if kwargs[x]]
        return self(args)


class CommandLineArgs(dict):
    POSITIONAL = 'start end timezone summary description'.split(' ')
    OPTIONAL = ('-a --calendar --location --url --format --alarms --repeat '
                '--until').split(' ')

    def __init__(self, timestamp_format='%Y-%m-%d %a %H:%M'):
        self.timestamp_format: str = timestamp_format
        for x in chain(self.POSITIONAL, self.OPTIONAL):
            self[x] = ''

    def load_from_org(self, item: OrgAgendaItem) -> 'CommandLineArgs':
        """TODO.

        Args:
            item:

        Returns
        -------

        """
        # For now, only 1 timestamp is supported
        time_stamp: NvimOrgDate = item.time_stamps[0]
        end: str = self._get_end(time_stamp)
        body: str = f':: {item.body}'
        key_vs_value: tuple = (
            ('start', time_stamp.start.strftime(self.timestamp_format)),
            ('end', end),
            ('summary', item.heading),
            ('description', body),
            ('--location', item.properties['LOCATION']),
            ('--url', item.properties['URL'])
        )
        for key, value in key_vs_value:
            self[key] = value

        return self

    def _get_end(self, time_stamp: NvimOrgDate) -> str:
        if time_stamp.has_end:
            return time_stamp.end.strftime(self.timestamp_format)
        else:
            return ''

    @classmethod
    def filter_positional(cls, obj: dict) -> dict:
        return {key: value for key, value in obj.items() if key in cls.POSITIONAL}

    @classmethod
    def filter_optional(cls, obj: dict) -> dict:
        return {key: value for key, value in obj.items() if key in cls.OPTIONAL}
