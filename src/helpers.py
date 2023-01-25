from argparse import ArgumentParser
from inspect import getfile
from os.path import dirname
from subprocess import check_output
from types import ModuleType
from typing import Any, Callable


def get_module_path(module: ModuleType) -> str:
    """Returns the path to the `module`.

    Args:
        module: a python module

    Returns
    -------
        str: path to module

    """
    return dirname(getfile(module))


class OrgToKhalArgumentParser(ArgumentParser):

    def __init__(self):
        super().__init__(
            prog='khal-orgmode',
            description='Interface between Khal and Orgmode.'
        )
        self.add_argument('calendar', type=str)
        self.add_argument('--logging', required=False, default='WARNING')


class SubProcessWithParser:

    def __init__(
            self,
            bin: str,
            parser: Callable = lambda: []) -> None:
        self.bin: str = bin
        self.parser: Callable = parser

    def __call__(self, args: tuple) -> str:
        args: list = self.parser(args)
        stdout: bytes = check_output([self.bin, *args])
        return stdout.decode()
