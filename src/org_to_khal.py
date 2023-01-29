import logging
from argparse import ArgumentParser

from src.khal_interface import (
    Calendar,
    CommandLineArgs,
)
from src.org_items import OrgAgendaItem


class CommandLineInterface(ArgumentParser):
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

    Returns:
        
    """
    logging.debug(f'Calendar is: {calendar_name}')
    calendar: Calendar = Calendar(calendar_name)
    org_item: OrgAgendaItem = OrgAgendaItem()
    khal_args: CommandLineArgs = CommandLineArgs()

    org_item.load_from_stdin()
    khal_args.load_from_org(org_item)
    stdout: str = calendar.new_item.from_dict(khal_args)
    return stdout
