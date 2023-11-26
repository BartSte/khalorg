from os.path import join
from unittest.mock import patch

from khalorg.khal.calendar import Calendar
from khalorg.org.agenda_items import OrgAgendaItem

from tests import static
from tests.agenda_items import Valid
from tests.helpers import get_module_path


def test_config_khal():
    return join(get_module_path(static), 'test_config_khal')


class Mixin:

    @patch('khalorg.khal.calendar.find_configuration_file', new=test_config_khal)
    def setUp(self) -> None:
        args: list = Valid.get_args()
        self.agenda_item: OrgAgendaItem = OrgAgendaItem(*args)
        self.calendar = Calendar('test_calendar')
