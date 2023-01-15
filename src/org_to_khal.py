import logging

from src.khal_interface import Commands
from src.org_items import OrgAgendaItem


def org_to_khal(calendar: str):
    logging.debug(f'Calendar is: {calendar}')
    khal_command: Commands = Commands(calendar)
    agenda_item: OrgAgendaItem = OrgAgendaItem()

    agenda_item.load_from_stdin()
    khal_command.new()
