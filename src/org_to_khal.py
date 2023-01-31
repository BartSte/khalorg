import logging
from argparse import ArgumentParser

from src.khal_items import (
    Args,
    Calendar,
)
from src.org_items import OrgAgendaItem


class CLI(ArgumentParser):
    """ TODO. """

    def __init__(self):
        """ TODO. """
        super().__init__(
            prog='khal-orgmode',
            description='Interface between Khal and Orgmode.'
        )
        self.add_argument('calendar', type=str)
        self.add_argument('--logging', required=False, default='WARNING')


def main(calendar_name: str) -> str:
    """TODO.

    Args:
        calendar_name:

    Returns
    -------

    """
    logging.debug(f'Calendar is: {calendar_name}')
    calendar: Calendar = Calendar(calendar_name)
    org_item: OrgAgendaItem = OrgAgendaItem()
    args: Args = Args()

    org_item.load_from_stdin()

    args['-a'] = calendar_name
    args.load_from_org(org_item)

    logging.debug(f'Command line args are: {args}')

    stdout: str = calendar.new_item(args.as_list())
    return stdout
