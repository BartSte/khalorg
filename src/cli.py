import logging
from argparse import ArgumentParser

from src.khal_items import (
    Calendar,
    KhalArgs,
)
from src.org_items import OrgAgendaItem


def get_parser() -> ArgumentParser:
    """TODO.

    Returns
    -------

    """
    
    parser: ArgumentParser = ArgumentParser(
        prog='khalorg',
        description='Interface between Khal and Orgmode.')

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

    parser.add_argument('--calendar', **calendar)
    parser.add_argument('--loglevel', **loglevel)
    subparsers = parser.add_subparsers()

    parser_new: ArgumentParser = subparsers.add_parser(
        'new', prog='khalorg new',
        description='Create a new khal item from an org item.')
    parser_new.set_defaults(func=new)

    parser_export: ArgumentParser = subparsers.add_parser(
        'export', prog='khalorg export',
        description='Export khal items to org items')
    parser_export.add_argument('start', **start)
    parser_export.add_argument('stop', **stop)
    parser_export.set_defaults(func=export)

    return parser


def new(calendar: str, **_) -> str:
    """Creates a new calendar item in a Khal calendar.

    It does this, by parsing an org agenda item, that is supplied through
    stdin, into a list of command line arguments. These arguments are used to
    invoke the `khal new` command by calling Calendar.new_item.

    Args:
        calendar_name: name of the khal calendar.

    Returns
    -------
        stdout

    """
    args: KhalArgs = KhalArgs()
    khal_calendar: Calendar = Calendar(calendar)
    org_item: OrgAgendaItem = OrgAgendaItem()

    org_item.load_from_stdin()
    args['-a'] = calendar
    args.load_from_org(org_item)

    logging.debug(f'Khal args are: {args}')
    return khal_calendar.new_item(args.as_list())


def export(calendar: str, start: str = 'today', stop: str = '1d', **_) -> str:
    """TODO.

    Args:
        calendar_name:
        start:
        stop:

    Returns
    -------

    """
    khal_calendar: Calendar = Calendar(calendar)
    args: list = ['-a', calendar, start, stop]
    logging.debug(f'Khal args are: {args}')
    return khal_calendar.export(args)
