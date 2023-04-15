import logging

from src.hacks import edit_attendees
from src.khal_items import Calendar, KhalArgs
from src.org_items import OrgAgendaItem
from src.post_processors import List


def list_command(
        calendar: str,
        start: str = 'today',
        stop: str = '1d',
        **_) -> str:
    """
    Lists khal agenda items to org format.

    Args:
        calendar: name of the khal calendar
        start: start date (default: today)
        stop: end date (default: 1d)

    Returns
    -------
        stdout of the `khal list` command after post processing

    """
    post_processor: List
    khal_calendar: Calendar = Calendar(calendar)

    args: list = ['-a', calendar, start, stop]
    org_items: str = khal_calendar.list_command(args)

    post_processor = List.from_str(org_items)
    return post_processor.remove_duplicates()


def new(calendar: str, **_) -> str:
    """
    Creates a new calendar item in a Khal calendar.

    It does this, by parsing an org agenda item, that is supplied through
    stdin, into a list of command line arguments. These arguments are used to
    invoke the `khal new` command by calling Calendar.new_item.

    Args:
        calendar: name of the khal calendar.

    Returns
    -------
        stdout of the `khal new` command

    """
    args: KhalArgs = KhalArgs()
    khal_calendar: Calendar = Calendar(calendar)
    org_item: OrgAgendaItem = OrgAgendaItem()

    org_item.load_from_stdin()
    args['-a'] = calendar
    args.load_from_org(org_item)

    logging.debug(f'Khal args are: {args}')
    stdout_khal: str = khal_calendar.new_item(args.as_list())

    # Only 1 org time stamp per org_item is supported for now
    edit_attendees(
        calendar,
        org_item.get_attendees(),
        args['summary'],
        org_item.time_stamps[0].start,
        org_item.time_stamps[0].end)
    return stdout_khal
