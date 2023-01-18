import logging

from src.khal_interface import Calendar
from src.org_items import OrgAgendaItem


def org_to_khal(calendar_name: str):
    logging.debug(f'Calendar is: {calendar_name}')
    calendar: Calendar = Calendar(calendar_name)
    agenda_item: OrgAgendaItem = OrgAgendaItem()

    agenda_item.load_from_stdin()
    calendar.new_item(agenda_item)
