from subprocess import check_output
from typing import Union

from khal.settings.settings import find_configuration_file, get_config

from src.org_items import NvimOrgDate, OrgAgendaItem


class Calendar:

    def __init__(self, name):
        path_config: Union[str, None] = find_configuration_file()
        self.config: dict = get_config(path_config)
        self.name: str = name
        self.new_item: NewItem = NewItem(calendar=name,
                                         timestamp_format=self.timestamp_format)  # noqa

    @property
    def timestamp_format(self) -> str:
        """longdatetimeformat.

        Returns
        -------

        """
        return self.config['locale']['longdatetimeformat']


class CalendarCommand:

    FORMAT: str = '%Y-%m-%d %a %H:%M'

    def __init__(
            self,
            bin: str = '',
            calendar: str = '',
            timestamp_format: str = FORMAT) -> None:

        self.bin: str = bin
        self.calendar: str = calendar
        self.timestamp_format: str = timestamp_format

    def from_org(self, item: OrgAgendaItem) -> str:
        """TODO

        Args:
            item: 

        Returns:
            
        """
        positional: dict = self.parse_positional(item)
        optional: dict = self.parse_optional(item)
        args: list = self.get_args(positional, optional)
        return self(args)

    def parse_positional(self, item: OrgAgendaItem) -> dict:
        """TODO

        Args:
            item: 

        Returns:
            
        """
        # For now, only 1 timestamp is supported
        time_stamp: NvimOrgDate = item.time_stamps[0]
        start: str = time_stamp.start.strftime(self.timestamp_format)

        if time_stamp.has_end:
            end: str = time_stamp.end.strftime(self.timestamp_format)
        else:
            end = ""

        summary: str = item.heading
        description: str = item.body

        return {'start': start,
                'end': end,
                'timezone': '',
                'summary': summary,
                'description': f':: {description}'}

    def parse_optional(self, item: OrgAgendaItem) -> dict:
        """TODO

        Args:
            item: 

        Returns:
            
        """
        return {'-a': self.calendar,
                '--calendar': self.calendar,
                '--location': item.properties['LOCATION'],
                '--url': item.properties['URL'],
                '--format': self.timestamp_format,
                '--alarms': '',
                '--repeat': '',
                '--until': ''}

    @staticmethod
    def get_args(positional: dict, optional: dict) -> list:
        """TODO

        Args:
            positional: 
            optional: 

        Returns:
            
        """
        # TODO indicate that this method needs to be overridden.
        return ['--help']

    def __call__(self, args: list) -> str:
        """TODO

        Args:
            args: 

        Returns:
            
        """
        stdout: bytes = check_output([self.bin, *args])
        return stdout.decode()


class NewItem(CalendarCommand):

    def __init__(
            self,
            calendar: str = '',
            timestamp_format: str = CalendarCommand.FORMAT) -> None:
        """TODO

        Args:
            calendar: 
            timestamp_format: 
        """
        super().__init__('khal new', calendar, timestamp_format)

    @staticmethod
    def get_args(positional: dict, optional: dict) -> list:
        """TODO

        Args:
            positional: 
            optional: 

        Returns:
            
        """
        keys_optional: list = '-a --location --url'.split(' ')
        keys_positional: list = 'start end timezone summary description'.split(' ')  # noqa

        args: list = [f'{x} {optional[x]}' for x in keys_optional]
        args += [positional[x] for x in keys_positional]
        return args
