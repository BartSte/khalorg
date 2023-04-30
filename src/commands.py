import logging
from datetime import date, datetime

from khal.controllers import Event

from src.helpers import get_khal_format, get_khalorg_format
from src.khal_items import Calendar, ListArgs, NewArgs
from src.org_items import OrgAgendaFile, OrgAgendaItem


class KhalorgError(Exception):
    """Raised when an error within Khalorg occurs."""


def list_command(
        calendar: str,
        khalorg_format: str = get_khalorg_format(),
        start: str = 'today',
        stop: str = '1d',
        **_) -> str:
    """
    Lists khal agenda items to org format.

    Args:
    ----
        calendar: name of the khal calendar
        start: start date (default: today)
        stop: end date (default: 1d)

    Returns:
    -------
        stdout of the `khal list` command after post processing

    """
    khal_calendar: Calendar = Calendar(calendar)
    args: ListArgs = ListArgs()

    args['-a'] = calendar
    args['-f'] = get_khal_format()
    args['start'] = start
    args['stop'] = stop

    org_items: str = khal_calendar.list_command(args.as_list())
    agenda: OrgAgendaFile = OrgAgendaFile.from_str(org_items)
    agenda.apply_rrules()
    return format(agenda, khalorg_format)


def new(calendar: str, until: str = '', **_) -> str:
    """
    Creates a new calendar item in a Khal calendar.

    It does this, by parsing an org agenda item, that is supplied through
    stdin, into a list of command line arguments. These arguments are used to
    invoke the `khal new` command by calling Calendar.new_item.

    Args:
    ----
        calendar: name of the khal calendar.
        until: Stop an event repeating on this date.

    Returns:
    -------
        stdout of the `khal new` command

    """
    args: NewArgs = NewArgs()
    khal_calendar: Calendar = Calendar(calendar)
    org_item: OrgAgendaItem = OrgAgendaItem()

    args['-u'] = until
    args['-a'] = calendar

    org_item.load_from_stdin()
    args.load_from_org(org_item)

    logging.debug(f'Khal args are: {args.as_list()}')
    stdout_khal: str = khal_calendar.new_item(args.as_list())

    # Only 1 org time stamp per org_item is supported for now
    attendees: list = org_item.get_attendees()
    start: datetime | date = org_item.timestamps[0].start
    end: datetime | date = org_item.timestamps[0].end

    if attendees:  # Attendees field is empty by default
        events: list[Event] = khal_calendar.get_events(args['summary'],
                                                       start,
                                                       end)
        message: str = 'Event summary and timestamp are duplicated.'
        assert len(events) <= 1, message

        try:
            event: Event = events.pop()
        except IndexError as error:
            message: str = 'New event could not be found.'
            raise KhalorgError(message) from error
        else:
            event.update_attendees(attendees)
            khal_calendar.update(event)

    return stdout_khal


def edit(calendar: str, **_) -> str:
    """
    Todo:
    ----
    ----.

    Args:
    ----
        calendar:
        **_:

    Returns:
    -------

    """
    # TODO write tests for edit command
    # Refactor new command
    # Refactor edit command
    khal_calendar: Calendar = Calendar(calendar)
    org_item: OrgAgendaItem = OrgAgendaItem()

    org_item.load_from_stdin()

    # Currently, 1 timestamp is supported.
    events: list[Event] = khal_calendar.get_events(
        org_item.title,
        org_item.timestamps[0].start,
        org_item.timestamps[0].end,
        org_item.properties.get('UID', '')
    )

    for event in events:
        event.update_url(org_item.properties.get('URL'))
        event.update_summary(org_item.title)
        event.update_location(org_item.properties.get('LOCATION', ''))
        event.update_attendees(org_item.properties.get('ATTENDEES', ''))
        event.update_categories(org_item.properties.get('CATEGORIES', ''))
        event.update_description(org_item.description)
        khal_calendar.update(event)

    return ''
