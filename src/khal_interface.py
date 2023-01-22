import subprocess
from typing import Callable, Union

from khal.settings.settings import find_configuration_file, get_config


class Calendar:

    def __init__(self, name):
        path_config: Union[str, None] = find_configuration_file()
        self.config: dict = get_config(path_config)
        self.name: str = name

        new_item_program: str = 'khal new'
        new_item_args: tuple = (
            'start',
            'end',
            'delta',
            'timezone',
            'summary',
            'description')
        new_item_options: tuple = (
            '--calendar',
            '--location',
            '--categories',
            '--repeat',
            '--until',
            '--format',
            '--alarms',
            '--url')

        self.dateformat: Callable = Command('khal printformats')
        self.new_item: Callable = Command(new_item_program,
                                          new_item_args,
                                          new_item_options)

    @property
    def long_datetime_format(self) -> str:
        return self.config['locale']['longdatetimeformat']


class Command:

    def __init__(
            self,
            program: str,
            args: tuple = tuple(),
            options: tuple = tuple()) -> None:

        self.program: str = program
        self.args: tuple = args
        self.options: tuple = options

    def __call__(self, args: tuple) -> str:
        stdout: bytes = subprocess.check_output([self.program, *args])
        return stdout.decode()

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
