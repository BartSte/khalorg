import logging
from configparser import ConfigParser
from inspect import getfile
from os import makedirs
from os.path import dirname
from subprocess import STDOUT, CalledProcessError, check_output
from types import ModuleType
from typing import Callable, Union

from munch import Munch


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
        return check_output(args, stderr=STDOUT)
    except CalledProcessError as error:
        error_message: str = (
            f"The following arguments were sent to khal:\n\n{' '.join(args)}"
            "\n\nNext, the following error was received from khal:\n\n"
            f"{error.output.decode()}\n\n")
        logging.critical(error_message)
        raise Exception(error_message) from error


class Config(ConfigParser):
    """ Exteds ConfigParser such that is easy to combine multiple config
    files.
    """

    def combine(self, destination: str, sources: Union[list, tuple]):
        """The `sources` are combined and saved as `destination`.

        Config files is `sources` with a higher index overwrite duplicated
        values of the others.

        Args:
        ----
            destination: the output is saved as a file
            sources: paths to config files
        """
        makedirs(dirname(destination), exist_ok=True)
        self.read(sources)
        with open(destination, 'w') as file_:
            self.write(file_)

    @property
    def as_munch(self) -> Munch:
        """Converts the ConfigParser object to Munch.

        Munch is more user friendly.

        Returns
        -------
            ConfigParser as Munch

        """
        return Munch.fromDict(self)  # pyright: ignore
