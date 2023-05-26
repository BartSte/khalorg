import logging
from collections import OrderedDict
from datetime import date, datetime
from typing import Callable, Generator, Iterable, TypedDict, Union

from khal.cli import build_collection
from khal.controllers import Event
from khal.khalendar import CalendarCollection
from khal.settings.settings import (
    ConfigObj,
    find_configuration_file,
    get_config,
)
from orgparse.date import OrgDate

from src.helpers import (
    get_khalorg_format,
    is_future,
    remove_tzinfo,
    subprocess_callback,
)
from src.org_items import OrgAgendaItem
from src.rrule import get_recurobject

Time = date | datetime


class CalendarProperties(TypedDict):
    """ Properties of a khal Event. """

    attendees: list[str]
    categories: list[str]
    description: str
    end: datetime | date
    location: str
    rrule: dict
    start: datetime | date
    summary: str
    uid: str
    url: str


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

    MESSAGE_EDIT: str = ('When trying to edit an event, the number of events '
                         'found was not 1 but: {}. The command was aborted.')

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
        list_args: list = ['khal', 'list', '-df', '', '-f', list_format]

        self._collection: CalendarCollection
        self._new_item: Callable = subprocess_callback(new_item_args)
        self._list_command: Callable = subprocess_callback(list_args)

        self.name: str = name
        self.config: dict = get_config(path_config)

    def new_item(self, khal_new_args: list) -> str:
        """
        Adds a new event to the calenadar.

        Runs `khal new` as a subprocess.

        Args:
        ----
            khal_new_args: command line args that would follow `khal new`.

        Returns:
        -------
            stdout of `khal new`
        """
        return self._new_item(khal_new_args)

    def list_command(self, khal_args: list) -> str:
        """
        Prints the khal items as org item using the `khalorg_format.txt`.

        Args:
        ----
            khal_args: list containing the command line arg that are send to
            `khal list`.

        Returns:
        -------
            stdout of the `khal list`
        """
        return self._list_command(khal_args)

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
        Returns the calendar collection of khal.

        It will be created once, and stored at `_collection`.


        Returns
        -------
            khal calendar collection.

        """
        if not hasattr(self, '_collection'):
            self._collection = get_calendar_collection(self.name)

        return self._collection

    def edit(self, props: CalendarProperties,
             edit_dates: bool = False) -> list[Event]:
        """
        Edit an existing event.

        The properties can be supplied through `props`.

        If the UID property is empty, the event will be located using its
        summary, start time, and end time. This may occur when an event is just
        created when using, for example, the `khalorg new` command.

        When editing a list of recurring events, khal will update the PROTO
        event, i.e., the series of events, not the occurence. Therefore, only
        the first event is send to `update_event`

        Args:
        ----
            props: typed dict containing agenda item properties
            edit_dates: If set to True, the org time stamp and its recurrence are
            also edited.

        Returns:
        -------
            the edited events

        """
        events: list[Event]

        if props['uid']:
            events = self.get_events(props['uid'])
        else:
            events = self.get_events_no_uid(props['summary'],
                                            props['start'],
                                            props['end'])

        events = [x for x in events if is_future(x.end, self.now())]

        if len(events) == 0:
            logging.error(self.MESSAGE_EDIT.format(len(events)))

        else:
            # Khal opdates the master/PROTO event (i.e., the series of events),
            # instead of only the occurence. Therefore, only 1 event needs to
            # be updated instead of the whole list.
            self.update_event(events[0], props, edit_dates)

        return events

    def now(self) -> datetime:
        """
        Returns datetime.now() for the local_timezone that is specified in
        the khal config.

        Returns
        -------
            now in the local timezone

        """
        return self.config['locale']['local_timezone'].localize(datetime.now())

    def update_event(
            self,
            event: Event,
            props: CalendarProperties,
            edit_dates: bool = False) -> Event:
        """
        Update an event with `props`.

        Args:
        ----
            event: the event
            props: a typed dict

        Returns:
        -------
            the update version of `event`

        """
        event.update_url(props['url'])
        event.update_summary(props['summary'])
        event.update_location(props['location'])
        event.update_attendees(props['attendees'])
        event.update_categories(props['categories'])
        event.update_description(props['description'])

        if edit_dates:
            event.update_start_end(props['start'], props['end'])
            event.update_rrule(props['rrule'])

        event.increment_sequence()
        self.collection.update(event)
        self.collection.update_db()

        return event

    def get_events(self, uid: str) -> list[Event]:
        """
        Returns events that share the same uid.

        Args:
        ----
            uid: unique identifier

        Returns:
        -------
            a list of events
        """
        # For unknown reasons, the CalendarCollection.search method cannot find
        # uids that are longer than 39 chars. Therefore, they are clipped and
        # filtered with a list comprehension later on.
        events: Iterable[Event] = self.collection.search(uid[-39:])
        return [x for x in events if x.uid == uid or not uid]

    def get_events_no_uid(
            self,
            summary_wanted: str,
            start_wanted: Time,
            end_wanted: Time) -> list[Event]:
        """
        Return events that share the same summary, start time and stop time.

        Timezone information is not supported yet, so it is ignored by setting
        the Event.end.tzinfo to None.

        Args:
        ----
            summary_wanted: summary/title of the event
            start_wanted: start time
            end_wanted: end time

        Returns:
        -------
            list of events
        """
        def exists(summary: str, end: Time) -> bool:
            equal_end: bool = remove_tzinfo(end) == remove_tzinfo(end_wanted)
            equal_summary: bool = summary == summary_wanted
            return equal_end and equal_summary

        logging.info(f'Get events on date: {start_wanted}')
        return [
            event for event in self.collection.get_events_on(start_wanted)
            if exists(event.summary, event.end)
        ]

    def update(self, event: Event) -> None:
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
        self.timezone: str = config['locale']['default_timezone']
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

        key_vs_value: tuple = (
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
        start: Time = self.add_tzinfo(org_item.first_timestamp.start)
        end: Time = self.add_tzinfo(org_item.first_timestamp.end)
        until: Time = self.add_tzinfo(org_item.until.start)
        repeater: tuple = org_item.first_timestamp._repeater or tuple()
        rule: dict = get_recurobject(start, repeater, until)

        props: CalendarProperties = CalendarProperties(
            start=start,
            end=end,
            rrule=rule,
            uid=str(org_item.properties.get('UID')),
            url=str(org_item.properties.get('URL')),
            summary=org_item.title,
            location=str(org_item.properties.get('LOCATION')),
            attendees=org_item.split_property('ATTENDEES'),
            categories=[str(org_item.properties.get('CATEGORIES'))],
            description=org_item.description,
        )
        self.update(props)

    def add_tzinfo(self, time: Time) -> Time:
        """Add tzinfo if possible.

        Args:
        ----
            time: a date of a datetime object

        Returns:
        -------
            `time` with an updated tzinfo if possible

        """
        try:
            return time.replace(tzinfo=self.timezone)  # type: ignore
        except (AttributeError, TypeError):
            return time
