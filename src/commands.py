import logging
import sys

from src.helpers import get_khal_format, get_khalorg_format
from src.khal_items import (
    Calendar,
    CalendarProperties,
    EditArgs,
    ListArgs,
    NewArgs,
)
from src.org_items import OrgAgendaFile, OrgAgendaItem


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

    Returns
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


def new(calendar: str, until: str = '', org: str = '', **_) -> str:
    """
    Creates a new calendar item in a Khal calendar.

    It does this, by parsing an org agenda item, that is supplied through
    stdin, into a list of command line arguments. These arguments are used to
    invoke the `khal new` command by calling Calendar.new_item. Alternatively,
    the org item can be supplied through the keyword arg `org`.

    After running the `khal new` command, properties are added to the event
    using the Calendar.edit command. These properties cannot be added through
    the `khal new` command, so this is a workaround.

    Args:
    ----
        calendar: name of the khal calendar.
        until: Stop an event repeating on this date.
        org: omit the stdin and send the input as an argument

    Returns
    -------
        stdout of the `khal new` command

    """
    org = org or sys.stdin.read()

    args_new: NewArgs = NewArgs()
    args_edit: EditArgs = EditArgs()
    khal_calendar: Calendar = Calendar(calendar)
    agenda_item: OrgAgendaItem = OrgAgendaItem()

    args_new['-u'] = until
    args_new['-a'] = calendar

    agenda_item.load_from_str(org)
    args_new.load_from_org(agenda_item)

    logging.debug(f'Khal new args are: {args_new.as_list()}')
    stdout_khal: str = khal_calendar.new_item(args_new.as_list())

    args_edit.load_from_org(agenda_item)
    args_edit['uid'] = ''  # new items should not have a uid
    logging.debug(f'Khal edit args are: {args_edit.as_list()}')
    khal_calendar.edit(CalendarProperties(**args_edit))

    return stdout_khal


def edit(calendar: str, org: str = '', **_) -> str:
    """Edit an existing khal agenda item.

    An existing khal agenda item is edited by supplying an org file with the
    desired properties. Empty fields are interpreted as being actuall empty and
    are thus not ignored.

    The org file can be supplied through stdin or through the `org` keyword
    argument.

    Ensure the correct UID is available in the UID properties otherwise the
    corresponding event cannot be found.

    Args:
    ----
        calendar: the name of the calendar.
        org: omit the stdin and send the input as an argument
        **_:
    """
    org = org or sys.stdin.read()

    args: EditArgs = EditArgs()
    khal_calendar: Calendar = Calendar(calendar)
    agenda_item: OrgAgendaItem = OrgAgendaItem()

    agenda_item.load_from_str(org)
    args.load_from_org(agenda_item)
    khal_calendar.edit(CalendarProperties(**args))
    return ''
