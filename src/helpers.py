from argparse import ArgumentParser
from inspect import getfile
from os.path import dirname
from types import ModuleType


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
