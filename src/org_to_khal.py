import logging
from argparse import ArgumentParser

from src.khal_items import (
    Args,
    Calendar,
)
from src.org_items import OrgAgendaItem


class CLI(ArgumentParser):
    """ Parser for org2khal. """

    def __init__(self):
        super().__init__(
            prog='khal-orgmode',
            description='Interface between Khal and Orgmode.'
        )

        command: dict = dict(
            type=str,
            choices=('new',),
            help=('Choose new if you want to add a new item.')
        )

        calendar: dict = dict(
            type=str,
            help=('Set the name of the khal calendar.')
        )

        logging: dict = dict(
            required=False,
            default='WARNING',
            help=('Set the logging level to: CRITICAL, WARNING (default), '
                  'INFO, DEBUG')
        )

        self.add_argument('command', **command)
        self.add_argument('calendar', **calendar)
        self.add_argument('--logging', **logging)


def main(command: str, calendar_name: str) -> str:
    """ Export an org agenda item to the khal calendar called `calendar_name`.

    Args:
        calendar_name: name of the khal calendar.

    Returns
    -------
        stdout of khal.

    """
    logging.debug(f'Calendar is: {calendar_name}')
    calendar: Calendar = Calendar(calendar_name)
    org_item: OrgAgendaItem = OrgAgendaItem()
    args: Args = Args()
    functions: dict = dict(new=calendar.new_item)

    org_item.load_from_stdin()

    args['-a'] = calendar_name
    args.load_from_org(org_item)

    logging.debug(f'Command line args are: {args}')

    stdout: str = functions[command](args.as_list())
    return stdout


