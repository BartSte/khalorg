import logging

from khal.cli import main_khal
from orgparse.node import OrgNode

from src.helpers import TempSysArgv
from src.org_items import OrgAgendaItem


def main():
    agenda_item: OrgAgendaItem = OrgAgendaItem()
    agenda_item = agenda_item.load_from_stdin()
    command: list = get_khal_command(agenda_item)
    with TempSysArgv(command) as argv:
        main_khal()


def get_khal_command(org) -> list:
    """

    Returns
    -------

    """
    return ['khal new', '--help']
