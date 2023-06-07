import logging
from datetime import date, datetime
from subprocess import STDOUT, CalledProcessError, check_output
from typing import Callable

from khalorg import paths

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


def is_future(timestamp: datetime | date) -> bool:
    """
    Whether the `timestamp` is in the future.

    Args:
    ----
        timestamp: the time

    Returns:
    -------
        True if the `timestamp` is in the future

    """
    if isinstance(timestamp, datetime):
        now: datetime = datetime.now(timestamp.tzinfo)
        return timestamp >= now
    else:
        return timestamp >= datetime.now().date()


def subprocess_callback(cmd: list) -> Callable:
    """
    Returns a subprocess.check_output callback where the `cmd` is defined
    beforehand.

    Args:
    ----
        cmd: the base command. For example: ['khal', 'new']

    Returns:
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


def remove_tzinfo(time: Time) -> Time:
    """
    Remove tzinfo if possible.

    Args:
    ----
        time: a date of a datetime object

    Returns:
    -------
        `time` without an updated tzinfo if possible

    """
    return time.replace(tzinfo=None) if isinstance(time, datetime) else time


def set_tzinfo(time: Time, timezone) -> Time:
    """
    Add tzinfo if possible.

    Args:
    ----
        time: a date of a datetime object
        tzinfo: timezone as str

    Returns:
    -------
        `time` with an updated tzinfo if possible

    """
    return timezone.localize(time) if isinstance(time, datetime) else time
