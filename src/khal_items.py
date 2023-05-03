import logging
from collections import OrderedDict
from datetime import date, datetime
from typing import Callable, Generator, Union

from khal.cli import build_collection
from khal.controllers import Event
from khal.khalendar import CalendarCollection
from khal.settings.settings import (
    ConfigObj,
    find_configuration_file,
    get_config,
)
from orgparse.date import OrgDate

from src.helpers import get_khalorg_format, subprocess_callback
from src.org_items import OrgAgendaItem

_Time = date | datetime


def get_calendar_collection(name: str) -> CalendarCollection:
    """
    Return the calendar collection for a specific calendar `name`.

    Args:
    ----
        name: name of the calendar

    Returns:
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
        list_format: str = get_khalorg_format()

        new_item_args: list = ['khal', 'new']
        list_args: list = ['khal', 'list', '--format', list_format]

        self._collection: CalendarCollection
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

    @property
    def collection(self) -> CalendarCollection:
        """
        Todo:
        ----
        ----.

        Returns:
        -------

        """
        if not hasattr(self, '_collection'):
            self._collection = get_calendar_collection(self.name)

        return self._collection

    def edit_item(self, org_item: OrgAgendaItem) -> None:
        """
        Todo:
        ----
        ----.

        Args:
        ----
            khal_calendar:
            org_item:
        """
        # Only 1 org time stamp per org_item is supported for now
        events: list[Event] = self.get_events(org_item)

        number_of_events: int = len(events)
        if number_of_events != 1:
            logging.warning(
                f'Number of events found was not 1 but: {number_of_events}'
            )

        for event in events:
            # categories is processed as list by khal intenals without needing
            # to split it based on its delimiters
            categories: list = [org_item.properties.get('CATEGORIES', '')]

            event.update_url(org_item.properties.get('URL'))
            event.update_summary(org_item.title)
            event.update_location(org_item.properties.get('LOCATION', ''))
            event.update_attendees(org_item.split_property('ATTENDEES'))
            event.update_categories(categories)
            event.update_description(org_item.description)
            self.collection.update(event)

    def get_events(self, org_items: OrgAgendaItem) -> list[Event]:
        """TODO

        Args:
            org_items: 

        Returns:
            
        """
        summary: str = org_items.title
        start: datetime | date = org_items.first_timestamp.start
        end: datetime | date = org_items.first_timestamp.end
        uid: str = org_items.properties.get('UID', '')

        logging.debug(f'Get events on date: {start}')
        events: Generator = (
            x for x in self.collection.get_events_on(start)
            if x.summary == summary and self._replace(x.end, tzinfo=None) == end
        )

        return [x for x in events if x.uid == uid or not uid]

    @staticmethod
    def _replace(obj: _Time, **kwargs) -> _Time:
        try:
            return obj.replace(**kwargs)
        except (AttributeError, TypeError):
            return obj

    def update(self, event: Event) -> None:
        """
        Todo:
        ----
        ----.

        Args:
        ----
            event:
        """
        self.collection.update(event)


class KhalArgsError(Exception):
    """Raised for an error in Args."""


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


class ListArgs(KhalArgs):
    """ Arguments for het `khal list` command. """

    pass


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

        key_vs_value: tuple = (
            ('start', time_stamp.start.strftime(format)),
            ('end', self._get_end(time_stamp, format)),
            ('summary', item.title),
            ('description', f':: {item.description}'),
            ('--location', item.properties.get('LOCATION', '')),
            ('--url', item.properties.get('URL', '')),
            ('--repeat', self._get_repeat(time_stamp))
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
        try:
            key: str = ''.join([str(x) for x in time_stamp._repeater])
            return self.REPEAT_ORG_TO_KHAL[key]
        except KeyError as error:
            message: str = f'The repeat value of: {key} is not supported.'
            raise KhalArgsError(message) from error
        except TypeError:  # no repeater found
            return ''
