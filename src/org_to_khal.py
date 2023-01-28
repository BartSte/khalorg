import logging

from src.khal_interface import Calendar, org_agenda_item_to_khal_cli_args
from src.org_items import OrgAgendaItem


def org_to_khal(calendar_name: str):
    logging.debug(f'Calendar is: {calendar_name}')
    calendar: Calendar = Calendar(calendar_name)
    org_item: OrgAgendaItem = OrgAgendaItem()

    org_item.load_from_stdin()
    stdout: str = calendar.new_item.from_org(org_item)
