import subprocess
from typing import Callable, Union

from khal.settings.settings import find_configuration_file, get_config


class Calendar:

    def __init__(self, name):
        path_config: Union[str, None] = find_configuration_file()
        self.config: dict = get_config(path_config)
        self.name: str = name

        self.new_item: Callable = NewItem()

    @property
    def long_datetime_format(self) -> str:
        """TODO.

        Returns
        -------

        """
        return self.config['locale']['longdatetimeformat']


class Command:

    def __init__(self, program: str) -> None:
        self.program: str = program

    def __call__(self, args: tuple) -> str:
        stdout: bytes = subprocess.check_output([self.program, *args])
        return stdout.decode()


class NewItem(Command):
    """The idea is that __call__ just wraps around subprocess.check_output. For
    each command a `from_org_org_argenda_item is created that does the parsing
    for each khal command.
    """

    def __init__(self) -> None:
        super().__init__('khal_new')

    def from_org_org_argenda_item(self) -> str:
        pass

        # """
        # Usage: khal new [OPTIONS] [START [END | DELTA] [TIMEZONE] [SUMMARY]
        # [:: DESCRIPTION]].
        # """
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

        # new_item_program: str = 'khal new'
        # new_item_args: tuple = (
        #     'start',
        #     'end',
        #     'delta',
        #     'timezone',
        #     'summary',
        #     'description')
        # new_item_options: tuple = (
        #     '--calendar',
        #     '--location',
        #     '--categories',
        #     '--repeat',
        #     '--until',
        #     '--format',
        #     '--alarms',
        #     '--url')
