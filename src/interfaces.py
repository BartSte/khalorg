from khal.cli import main_khal

from src.helpers import TempSysArgv


class Khal:
    def __init__(self, calendar=''):
        self.calendar: str = calendar

    def new(self):
        """

        Returns
        -------

        """
        self._execute(['khal new', '--help'])

    def _execute(self, command: list):
        with TempSysArgv(command) as argv:
            main_khal()
