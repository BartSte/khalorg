from khal.cli import main_khal

from src.helpers import TempSysArgv
from src.org_items import OrgAgendaItem


class Calendar:

    def __init__(self, name):
        self.name: str = name

    def new_item(self, item: OrgAgendaItem):
        """
        Usage: khal new [OPTIONS] [START [END | DELTA] [TIMEZONE] [SUMMARY]
        [:: DESCRIPTION]].
        """
        options: tuple[tuple[str, str], ...] = (
            ('--calendar', self.name),
            ('--location', item.properties['location']),
            ('--categories', ''),
            ('--repeat', ''),
            ('--until', ''),
            ('--format', ),
            ('--alarms', ),
            ('--url' item.properties['URL'])
        )
        command: list = ['khal new']
        optional: list = [ f'{x} {y}' for x, y in options if y]
        positional: list = [
            ''
        ]

        self._execute(command)

    def _execute(self, command: list):
        with TempSysArgv(command) as argv:
            main_khal()
