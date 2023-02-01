from inspect import getfile
import logging
from os.path import dirname
from subprocess import CalledProcessError, check_output
from types import ModuleType
from typing import Callable, Iterable


def get_module_path(module: ModuleType) -> str:
    """Returns the path to the `module`.

    Args:
        module: a python module

    Returns
    -------
        str: path to module

    """
    return dirname(getfile(module))


def subprocess_callback(cmd: list) -> Callable:
    """Returns a subprocess.check_output callback where the `cmd` is defined
    beforehand.

    Args:
        cmd: the base command. For example: ['khal', 'new']

    Returns
    -------
        callback function

    """
    def callback(args: list) -> str:
        return try_check_output([*cmd, *args]).decode()

    return callback

def try_check_output(args: list) -> bytes:
    try:
        return check_output(args)
    except CalledProcessError as error:
        logging.critical(error.output)
        raise Exception('Fail.') from error
