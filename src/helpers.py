import logging
import re
from configparser import ConfigParser
from datetime import date, datetime
from inspect import getfile
from os.path import dirname, exists
from subprocess import STDOUT, CalledProcessError, check_output
from types import ModuleType
from typing import Callable

from munch import Munch

import paths

Time = date | datetime


def get_khal_format():
    """
    Returns the format that is used for the `khal list --format` command
    that is used within the `khalorg list` command.

    Returns
    -------
        the khal list format

    """
    with open(paths.khal_format) as file_:
        return file_.read()


def get_default_khalorg_format() -> str:
    """
    Returns the default format for the `khalorg list --format` option.

    Returns
    -------
       the format as a str
    """
    with open(paths.default_format) as file_:
        return file_.read()


def get_khalorg_format():
    """
    Returns the user specified `khalorg list --format` optional argument.
    This format should be stored at the `~/.config/khalorg/khalorg_format.txt`
    file. This file does not exists untill it is created by the user.

    Returns
    -------
        the user-specific format.

    """
    path: str = paths.format if exists(paths.format) else paths.default_format
    with open(path) as file_:
        return file_.read()


def get_module_path(module: ModuleType) -> str:
    """
    Returns the path to the `module`.

    Args:
    ----
        module: a python module

    Returns
    -------
        str: path to module

    """
    return dirname(getfile(module))


def subprocess_callback(cmd: list) -> Callable:
    """
    Returns a subprocess.check_output callback where the `cmd` is defined
    beforehand.

    Args:
    ----
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


def get_config(sources: list) -> Munch:
    """
    Reads the config files in `sources` and converts them to a Munch object.

    Returns
    -------
        ConfigParser object as Munch
    """
    config: ConfigParser = ConfigParser()
    config.read(sources)
    return Munch.fromDict(config)  # pyright: ignore


def substitude_with_placeholder(text: str, callback: Callable,
                                start_placeholder: str = 'KHALORG_START',
                                stop_placeholder: str = 'KHALORG_STOP') -> str:
    """
    Replace all occurrences of a substring between two placeholders in a given
    string with the output of a specified callback function. The regex
    groupname or the text within the placeholders is "content".

    Args:
    ----
        text (str): The original string containing the substrings to be
            replaced.
        callback (Callable): A function that takes a substring as input and
            returns a replacement string.
        start_placeholder (str, optional): The starting placeholder string.
            Defaults to 'KHALORG_START'.
        stop_placeholder (str, optional): The ending placeholder string.
            Defaults to 'KHALORG_STOP'.

    Returns
    -------
        str: The modified string with all substrings replaced.
    """
    regex: str = rf'(?:{start_placeholder})(?P<content>.*?)(?:{stop_placeholder})'
    return re.sub(regex, callback, text)


def get_indent(text: str, piece: str) -> list:
    """
    Returns the indent for a `piece` of `text`. If `piece` is found multiple
    times, the returned list has a length that is larger than one.

    Args:
    ----
        text: the text
        piece: the str that needs to be found.

    Returns
    -------
        the indents that belong to the matches.

    """
    return re.findall(rf'^(\s+){piece}', text, re.MULTILINE)


def is_future(timestamp: datetime | date, now: datetime):
    """
    Whether the `timestamp` is in the future.

    Args:
    ----
        timestamp: the time
        now: the current time

    Returns
    -------
        True if the `timestamp` is in the future

    """
    if isinstance(timestamp, datetime):
        result: bool = timestamp >= now
    else:
        result: bool = timestamp >= now.date()

    if not result:
        logging.warning('Editing past events is not supported.')

    return result


def remove_tzinfo(time: Time) -> Time:
    """Remove tzinfo if possible.

    Args:
    ----
        time: a date of a datetime object

    Returns
    -------
        `time` without an updated tzinfo if possible

    """
    return time.replace(tzinfo=None) if isinstance(time, datetime) else time


def set_tzinfo(time: Time, timezone) -> Time:
    """Add tzinfo if possible.

    Args:
    ----
        time: a date of a datetime object
        tzinfo: timezone as str

    Returns
    -------
        `time` with an updated tzinfo if possible

    """
    return timezone.localize(time) if isinstance(time, datetime) else time
