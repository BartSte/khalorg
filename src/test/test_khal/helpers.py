from test.agenda_items import Valid

from khalorg.khal.calendar import Calendar
from khalorg.org.agenda_items import OrgAgendaItem


class Mixin:

    def setUp(self) -> None:
        args: list = Valid.get_args()
        self.agenda_item: OrgAgendaItem = OrgAgendaItem(*args)
        self.calendar = Calendar('test_calendar')
