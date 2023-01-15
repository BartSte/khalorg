import logging

from src.interfaces import Khal
from src.org_items import OrgAgendaItem


def org_to_khal(calendar: str):
    logging.debug(f'Calendar is: {calendar}')
    khal: Khal = Khal(calendar)
    agenda_item: OrgAgendaItem = OrgAgendaItem()

    agenda_item.load_from_stdin()
    khal.new()
