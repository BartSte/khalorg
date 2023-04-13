import logging
from argparse import ArgumentParser
from datetime import datetime

from khal.khalendar import khalendar

from src.hacks import edit_attendees
from src.khal_items import Calendar, KhalArgs
from src.org_items import OrgAgendaItem
from src.post_processors import Export


def get_parser() -> ArgumentParser:
    """
    Returns an ArgumentParser object for khalorg.

    Returns
    -------
        an ArgumentParser object.

    """
    parent: ArgumentParser = ArgumentParser(**ParserInfo.parent)
    parent.add_argument('--loglevel', **Args.loglevel)
    subparsers = parent.add_subparsers()

    child_new: ArgumentParser = subparsers.add_parser('new', **ParserInfo.new)
    child_new.add_argument('calendar', **Args.calendar)
    child_new.set_defaults(func=new)

    child_export: ArgumentParser = subparsers.add_parser('export',
                                                         **ParserInfo.export)
    child_export.add_argument('calendar', **Args.calendar)
    child_export.add_argument('start', **Args.start)
    child_export.add_argument('stop', **Args.stop)
    child_export.set_defaults(func=export)

    return parent


class ParserInfo:
    """ Constructor arguments for the ArgumentParser objects."""

    parent: dict = dict(
        prog='khalorg',
        description='Interface between Khal and Orgmode.')

    new: dict = dict(
        prog='khalorg new',
        description='Create a new khal item from an org item.')

    export: dict = dict(
        prog='khalorg export', description='Export khal items to org items')


class Args:
    """ Arguments for the ArgumentParser.add_argument methods."""

    calendar: dict = dict(
        type=str,
        help=('Set the name of the khal calendar.')
    )

    loglevel: dict = dict(
        required=False,
        default='WARNING',
        help=('Set the logging level to: CRITICAL, ERROR, WARNING '
              '(default), INFO, DEBUG')
    )

    start: dict = dict(
        type=str,
        default='today',
        nargs='?',
        help=('Start date (default: today)'))

    stop: dict = dict(
        type=str,
        default='1d',
        nargs='?',
        help=('End date (default: 1d)'))


def export(calendar: str, start: str = 'today', stop: str = '1d', **_) -> str:
    """
    Exports khal agenda items to org format.

    Args:
        calendar: name of the khal calendar
        start: start date (default: today)
        stop: end date (default: 1d)

    Returns
    -------
        stdout of the `khal list` command after post processing

    """
    post_processor: Export
    khal_calendar: Calendar = Calendar(calendar)

    args: list = ['-a', calendar, start, stop]
    org_items: str = khal_calendar.export(args)

    post_processor = Export.from_str(org_items)
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
