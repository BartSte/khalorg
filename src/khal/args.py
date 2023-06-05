import logging
from collections import OrderedDict
from datetime import date, datetime
from typing import Generator

from khal.settings.settings import (
    find_configuration_file,
    get_config,
)
from orgparse.date import OrgDate

from src.khal.calendar import CalendarProperties
from src.khal.helpers import set_tzinfo
from src.org.agenda_items import OrgAgendaItem
from src.rrule import get_recurobject

Time = date | datetime


class KhalArgs(OrderedDict):
    """
    Represents the command line arguments and options as an OrderedDict.

    Any argument can be added to the dictionary. If the key of the dictionary
    is prepended with a hyphen, it is interpreted as an option so its key-value
    pair is returned when calling `KhalArgs.as_list`. Otherwise, it is
    interpreted as a positional argument. Entries with a value that satisfy
    `bool(value) == False` are ignored.

    For example:
    ```
    args: KhalArgs = KhalArgs()
    args['-x'] = 'foo'
    args['--bar'] = 'bar'
    argr['--baz'] = ''
    args['one'] = 'first'
    args['two'] = 'second'
    args['three'] = ''
    print(args.as_list())

    >> ['-x', 'foo', '--bar', 'bar', 'first', 'second']
    ```

    Attributes
    ----------
        date_format: date format that is specified in the khal config.
        datetime_format: datetime format that is specified in the khal config
    """

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
        self.timezone = config['locale']['default_timezone']
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


class NewArgs(KhalArgs):
    """
    Loads the command line arguments for the `khal new` command
    directly from an org file.
    """

    def load_from_org(self, item: OrgAgendaItem) -> 'NewArgs':
        """
        For convenience: directly load Args from OrgAgendaItem.

        Load the command line arguments for khal into Args (which is an
        OrderedDict) directly from an OrgAgendaItem.

        Args:
        ----
            item: an OrgAgendaItem object.
            datetime_format: optionally, a timestamp format can be provided.

        Returns:
        -------
            itself

        """
        if item.first_timestamp.has_time():
            format: str = self.datetime_format
        else:
            format: str = self.date_format

        return self._load_from_org(item.first_timestamp, item, format)

    def _load_from_org(self,
                       time_stamp: OrgDate,
                       item: OrgAgendaItem,
                       format: str) -> 'NewArgs':

        key_vs_value: tuple[tuple[str, datetime | str], ...] = (
            ('start', time_stamp.start.strftime(format)),
            ('end', self._get_end(time_stamp, format)),
            ('summary', item.title),
            ('description', f':: {item.description}'),
            ('--location', item.properties.get('LOCATION', '')),
            ('--url', item.properties.get('URL', '')),
            ('--repeat', self._get_repeat(time_stamp)),
            ('--until', item.properties.get('UNTIL', ''))
        )

        for key, value in key_vs_value:
            if value:
                self[key] = value

        return self

    def _get_end(self, time_stamp: OrgDate, format: str) -> str:
        """
        Returns the start time if no end time exists.

        Args:
        ----
            time_stamp: the end time
            format: format

        Returns:
        -------
            timestamp as a str
        """
        try:
            return time_stamp.end.strftime(format)
        except AttributeError:
            logging.debug('End timestamp cannot be formatted.')
            return time_stamp.start.strftime(format)

    def _get_repeat(self, time_stamp: OrgDate) -> str:
        """
        Return the repeat in the `time_stamp` as an iCal RRULE. NewArgs only
        supports: daily, weekly, monthly, and yearly.

        Args:
        ----
            time_stamp: an OrgDate time stamp

        Returns:
        -------
            iCal RRULE
        """
        try:
            key: str = ''.join([str(x) for x in time_stamp._repeater])
            return self.REPEAT_ORG_TO_KHAL.get(key, '')
        except TypeError:
            logging.debug('No repeater found.')
            return ''


class EditArgs(KhalArgs):
    """ Arguments for the Calendar.edit command. """

    def load_from_org(self, org_item: OrgAgendaItem):
        """
        Loads the org file such that it can be used as an input for the
        Calendar.edit command.

        Args:
        ----
            org_item: the org agenda item
        """
        timestamp: OrgDate = org_item.first_timestamp

        start: Time = set_tzinfo(timestamp.start, self.timezone)
        end: Time = set_tzinfo(timestamp.end, self.timezone)
        until: Time = set_tzinfo(org_item.until.start, self.timezone)

        repeater: tuple[str, int, str] = org_item.first_timestamp._repeater or tuple()
        rule: dict = get_recurobject(start, repeater, until)

        props: CalendarProperties = CalendarProperties(
            start=start,
            end=end or start,
            rrule=rule or None,
            uid=str(org_item.properties.get('UID', '')),
            url=str(org_item.properties.get('URL', '')),
            summary=org_item.title,
            location=str(org_item.properties.get('LOCATION', '')),
            attendees=org_item.split_property('ATTENDEES'),
            categories=[str(org_item.properties.get('CATEGORIES', ''))],
            description=org_item.description,
        )
        self.update(props)


class DeleteArgs(EditArgs):
    """Arguments for the Calendar.delete command."""

    pass
