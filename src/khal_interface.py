from typing import Callable
from khal.cli import main_khal

from src.helpers import TempSysArgv
from src.org_items import OrgAgendaItem


class Calendar:

    def __init__(self, name):
        self.name: str = name

        new_item_args: tuple = (
            'start',
            'end',
            'delta',
            'timezone',
            'summary',
            'description'
        )

        new_item_options: tuple = (
            '--calendar',
            '--location',
            '--categories',
            '--repeat',
            '--until',
            '--format',
            '--alarms',
            '--url')

        self.new_item: Callable = Command(
            program='khal new',
            args=new_item_args,
            options=new_item_options)


class Command:

    def __init__(
            self,
            program: str,
            args: tuple = tuple(),
            options: tuple = tuple()):

        self.program: str = program
        self.args: tuple = args
        self.options: tuple = options

    def __call__(self, args: tuple, optional: dict = {}):
        """
        Usage: khal new [OPTIONS] [START [END | DELTA] [TIMEZONE] [SUMMARY]
        [:: DESCRIPTION]].
        """
        pass
        # options: tuple[tuple[str, str], ...] = (
        #     ('--calendar', self.name),
        #     ('--location', item.properties['location']),
        #     ('--categories', ''),
        #     ('--repeat', ''),
        #     ('--until', ''),
        #     ('--format', ),
        #     ('--alarms', ),
        #     ('--url' item.properties['URL'])
        # )
        # command: list = ['khal new']
        # optional: list = [f'{x} {y}' for x, y in options if y]
        # positional: list = [
        #     ''
        # ]

        # self._execute(command)

    def _execute(self, command: list):
        with TempSysArgv(command) as argv:
            main_khal()
