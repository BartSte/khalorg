import logging
from datetime import date, datetime
from typing import Callable, Iterable, TypedDict, Union

from khal.cli import build_collection
from khal.controllers import Event
from khal.khalendar import CalendarCollection
from khal.khalendar.vdir import NotFoundError
from khal.settings.settings import (
    ConfigObj,
    find_configuration_file,
    get_config,
)

from khalorg.khal.helpers import (
    is_future,
    remove_tzinfo,
    subprocess_callback,
)

Time = date | datetime


class CalendarProperties(TypedDict):
    """ Properties of a khal Event. """

    attendees: list[str]
    categories: list[str]
    description: str
    end: datetime | date
    location: str
    rrule: dict | None
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

    MESSAGE_EDIT: str = ('When trying to edit an event, the number of events '
                         'found in the khal calendar was not 1 but: {}. The '
                         'command was aborted.')

    MESSAGE_DELETE: str = (
        'When trying to delete an event, the number of events'
        ' found in the khal calendar was not 1 but: {}. The '
        'command was aborted.')

    def __init__(self, name: str):
        """
        Init.

        Args:
        ----
            name: name of the khal calendar
        """
        path_config: Union[str, None] = find_configuration_file()

        new_item_args: list = ["python3", "-m", "khal", "new"]
        list_args: list = ["python3", "-m", "khal", "list", "-df", ""]

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

        Returns
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

        Returns
        -------
            stdout of the `khal list`
        """
        logging.info(f'khalorg list args are: {khal_args}')
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

        Returns
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

        logging.info(f'number of events is {len(events)}')
        events = [x for x in events if is_future(x.end)]

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
        return self.config['locale']['default_timezone'].localize(
            datetime.now())

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

        Returns
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

        Returns
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

        Returns
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

    def exists(
            self,
            summary_wanted: str,
            start_wanted: Time,
            end_wanted: Time) -> bool:
        """
        Returns True if an item exists at this specific time, with the same
        title.
        """
        events: list = self.get_events_no_uid(
            summary_wanted,
            start_wanted,
            end_wanted
        )
        return len(events) > 0

    def delete(self, props: CalendarProperties) -> str:
        """Deletes an event from the Calendar.collection. The whole series is
        removed.

        Args:
        ----
            props: dictionary representing the event.
        """
        events: list = self.get_events(props['uid'])

        if len(events) == 0:
            logging.error(self.MESSAGE_DELETE.format(len(events)))
        else:
            # For now, the whole series is repmoved.
            event = events[0]
            assert event.href is not None
            try:
                self.collection.delete(event.href,
                                       event.etag,
                                       calendar=event.calendar)
            except NotFoundError as error:
                logging.error(error)
            finally:
                return ''
