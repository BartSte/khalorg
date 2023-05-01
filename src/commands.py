import logging

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

    # attendees are added after the `khal new` command.
    if org_item.split_property('ATTENDEES'):  # Attendees field is empty by default
        khal_calendar.edit_item(org_item)

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
    # TODO write tests for new command
    # TODO write tests for edit command
    # Refactor new command
    # Refactor edit command
    khal_calendar: Calendar = Calendar(calendar)
    org_item: OrgAgendaItem = OrgAgendaItem()

    org_item.load_from_stdin()
    khal_calendar.edit_item(org_item)

    return ''
