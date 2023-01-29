from inspect import getfile
from os.path import dirname
from subprocess import check_output
from types import ModuleType
from typing import Callable


def get_module_path(module: ModuleType) -> str:
    """Returns the path to the `module`.

    Args:
        module: a python module

    Returns
    -------
        str: path to module

    """
    return dirname(getfile(module))


def subprocess_callback(cmd) -> Callable:
    """TODO.

    Args:
        cmd ():

    Returns
    -------

    """
    def callback(args: list) -> str:
        return check_output([cmd, *args]).decode()

    return callback
