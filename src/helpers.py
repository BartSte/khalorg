import logging
import sys
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


class TempSysArgv:
    """
    The `new` command of khal in not exposed as a function that can easily be called
    from a script. A simpler solution is to temporary change sys.argv so it contains
    the desired command line arguments.

    Attributes
    ----------
        old:
        new:
        argv:
        argv:
    """

    def __init__(self, argv: list):
        """

        Args:
        ----
            argv (list):
        """
        self.old: list = sys.argv
        self.new: list = argv

        message: str = f"sys.argv will temporary be replaced by: {argv}"
        logging.info(message)

    def __enter__(self):
        """

        Args:
        ----
            self ():
        """
        sys.argv = self.new
        logging.debug(f'Sys argv is set to: {sys.argv}')
        return self

    def __exit__(self, *_):
        """

        Args:
        ----
            self ():
            *_:
        """
        sys.argv = self.old
        logging.debug(f'Sys argv is reset to: {sys.argv}')


class OrgToKhalParser(ArgumentParser):
    
    def __init__(self):
        super().__init__(
            prog='khal-orgmode',
            description='Interface between Khal and Orgmode.'
        )
        self.add_argument('calendar', type=str)
        self.add_argument('--logging', required=False, default='WARNING')

