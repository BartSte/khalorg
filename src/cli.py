import logging
from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
from collections import defaultdict
from os.path import join

from paths import config_dir, static_dir
from src.khal_items import (
    Calendar,
    KhalArgs,
)
from src.org_items import OrgAgendaItem


def main(command: str,
         calendar: str,
         loglevel: str = 'WARNING',
         **kwargs) -> str:
    """ Export an org agenda item to the khal calendar called `calendar_name`.

    Args:
        command: command as a string: new or export.
        calendar: name of the khal calendar.

    Returns
    -------
        stdout of khal.

    """
    logging.basicConfig(level=loglevel)
    logging.debug(f'Command is: {command}')
    logging.debug(f'Calendar is: {calendar}')
    logging.debug(f'Config directory is: {config_dir}')
    logging.debug(f'kwargs are: {kwargs}')

    functions: dict = dict(new=new, export=export)
    return functions[command](calendar, **kwargs)


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


def export(calendar_name: str, start: str = 'today', stop: str = '2d') -> str:
    """TODO.

    Args:
        calendar_name:
        start:
        stop:

    Returns
    -------

    """
    calendar: Calendar = Calendar(calendar_name)
    return calendar.export(['-a', calendar_name, start, stop])


def get_parser() -> ArgumentParser:
    """TODO.

    Returns
    -------

    """
    parent_parser: ParentParser = ParentParser(add_help=False)
    parent_parser_with_help: ParentParser = ParentParser()

    parsers: defaultdict = defaultdict(lambda: parent_parser_with_help)
    parsers['export'] = ExportParser(parents=[parent_parser])

    args: Namespace = parent_parser_with_help.parse_args()
    return parsers[args.command]


class ParentParser(ArgumentParser):
    """ Parser for khalorg. """

    def __init__(self, **kwargs):
        """ TODO. """
        path_epilog: str = join(static_dir, 'epilog.txt')
        with open(path_epilog) as file_:
            epilog: str = file_.read()

        super().__init__(
            prog='khal-orgmode',
            description='Interface between Khal and Orgmode.',
            formatter_class=RawDescriptionHelpFormatter,
            epilog=epilog,
            **kwargs
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

        loglevel: dict = dict(
            required=False,
            default='WARNING',
            help=('Set the logging level to: CRITICAL, ERROR, WARNING '
                  '(default), INFO, DEBUG')
        )

        arguments: tuple = ('command', 'calendar', '--loglevel')
        settings: tuple = (command, calendar, loglevel)
        for argument, kwargs in zip(arguments, settings):
            self.add_argument(argument, **kwargs)


class ExportParser(ArgumentParser):

    def __init__(self, parents: list) -> None:
        """TODO.

        Args:
        ----
            parents:
        """
        super().__init__(parents=parents)

        start: dict = dict(
            type=str,
            default='today',
            nargs='?',
            help=('TODO'))

        stop: dict = dict(
            type=str,
            default='2d',
            nargs='?',
            help=('TODO'))

        self.add_argument('start', **start)
        self.add_argument('stop', **stop)
