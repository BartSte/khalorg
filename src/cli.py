import logging
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from os.path import join

from paths import config_dir, static_dir
from src.khal_items import (
    Calendar,
    KhalArgs,
)
from src.org_items import OrgAgendaItem


def main(command: str, calendar_name: str) -> str:
    """ Export an org agenda item to the khal calendar called `calendar_name`.

    Args:
        calendar_name: name of the khal calendar.

    Returns
    -------
        stdout of khal.

    """
    logging.debug(f'Command is: {command}')
    logging.debug(f'Calendar is: {calendar_name}')
    logging.debug(f'Config directory is: {config_dir}')
    functions: dict = dict(new=new, export=export)
    return functions[command](calendar_name)


def new(calendar_name: str) -> str:
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
    calendar: Calendar = Calendar(calendar_name)
    org_item: OrgAgendaItem = OrgAgendaItem()

    org_item.load_from_stdin()
    args['-a'] = calendar_name
    args.load_from_org(org_item)

    logging.debug(f'Command line args are: {args}')
    return calendar.new_item(args.as_list())


def export(calendar_name: str) -> str:
    """TODO

    Args:
        calendar_name: 

    Returns:
        
    """
    args: KhalArgs = KhalArgs()
    calendar: Calendar = Calendar(calendar_name)
    args['-a'] = calendar_name
    return calendar.export(args.as_list())


class KhalOrgParser(ArgumentParser):
    """ Parser for khalorg. """

    def __init__(self):

        path_epilog: str = join(static_dir, 'epilog.txt')
        with open(path_epilog) as file_:
            epilog: str = file_.read()

        super().__init__(
            prog='khal-orgmode',
            description='Interface between Khal and Orgmode.',
            formatter_class=RawDescriptionHelpFormatter,
            epilog=epilog
        )

        command: dict = dict(
            type=str,
            choices=('export', 'new',),
            help=('Choose one of these commands. More info is provided below')
        )

        calendar: dict = dict(
            type=str,
            help=('Set the name of the khal calendar.')
        )

        logging: dict = dict(
            required=False,
            default='WARNING',
            help=('Set the logging level to: CRITICAL, ERROR, WARNING '
                  '(default), INFO, DEBUG')
        )

        self.add_argument('command', **command)
        self.add_argument('calendar', **calendar)
        self.add_argument('--logging', **logging)
