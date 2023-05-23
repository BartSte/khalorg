import re
from datetime import date

from dateutil.rrule import (
    DAILY,
    HOURLY,
    MONTHLY,
    WEEKLY,
    YEARLY,
    rrule,
    rruleset,
    rrulestr,
)
from icalendar.prop import vRecur
from orgparse.date import OrgDate

MAX_WEEKDAYS: int = 2
NOT_SUPPORTED: tuple = (
    '_byeaster',
    '_bymonthday',
    '_bynmonthday',
    '_bynweekday',
    '_bysetpos',
    '_byweekno',
    '_byyearday')


def get_recurobject(date: OrgDate,
                    until: OrgDate | None = None) -> dict:
    """Retruns the RRULE as an iCal vRecur object.

    Args:
        date: start date
        until: end date of recurrence rule

    Returns:
        vRecur object that represents the RRULE
    """
    return vRecur.from_ical(get_rrulestr(date, until, clip=True))


def get_rrulestr(date: OrgDate,
                 until: OrgDate | None = None,
                 clip: bool = False) -> str:
    """Return the rrule as a str.

    By setting `clip` to true, the string is compatible for vRecur.from_ical.

    Args:
        date: start date
        until: end date of recurrence rule
        clip: substitude part of the str that makes it incompatible with the
        vRecur.from_ical function

    Returns:
        RRULE as str 
    """
    try:
        return _get_rrulestr(date, until, clip=clip)
    except RRuleError:
        return ''


def _get_rrulestr(
        date: OrgDate,
        until: OrgDate | None = None,
        clip: bool = False) -> str:

    """Same as get_rrule but without a try-except.

    Args:
        date: start date
        until: end date of recurrence rule
        clip: substitude part of the str that makes it incompatible with the
        vRecur.from_ical function

    Returns:
        RRULE as str 
    """
    result: str = str(get_rrule(date, until))
    return re.sub(r'^DTSTART:.*\nRRULE:', '', result) if clip else result


def get_rrule(date: OrgDate, until: OrgDate | date | None = None) -> rrule:
    """Retruns the RRULE as an rrule of the dateutils module.

    Args:
        date: start date
        until: end date of recurrence rule

    Returns:
        rrule object that represents the RRULE
    """
    if isinstance(until, OrgDate):
        until = until.start

    result: rrule = rrule(
        freq=get_rrule_freq(date),
        dtstart=date.start,
        interval=get_rrule_interval(date),
        until=until
    )
    return result


def get_rrule_freq(date: OrgDate) -> int:
    """Converst the OrgDate repeater to an RRULE frequency.

    Args:
        date: start date

    Returns:
        the RRULE frequency.
    """
    freq_map: dict = {
        'y': YEARLY,
        'm': MONTHLY,
        'w': WEEKLY,
        'd': DAILY,
        'h': HOURLY
    }
    try:
        key: str = date._repeater[2]
        return freq_map[key]
    except (IndexError, KeyError, TypeError) as error:
        raise RRuleError("Unsupported RRULE") from error


class RRuleError(Exception):
    """Unsupported RRule encountered."""


def get_rrule_interval(date: OrgDate) -> int:
    """Return the RRULE interval.

    Args:
        date: start date

    Returns:
        the RRULE interval
    """
    try:
        interval: int = date._repeater[1]
        assert isinstance(interval, int)
        return interval
    except (IndexError, TypeError, AssertionError) as error:
        raise RRuleError("Unsupported RRULE") from error


def set_org_repeater(
        date: OrgDate,
        rule: str,
        allow_short_range: bool = False) -> OrgDate:
    """
    Apply the repeater of `date` that corresponds to the `rrule`.

    Args:
    ----
        date: the org date
        rule: the rrule str
        allow_short_range: see documentation of OrgDate.

    Returns
    -------
        the `date` with the repeater that corresponds to `rrule`.
    """
    obj: OrgDate = OrgDate(
        start=date.start,
        end=date.end,
        active=True,
        repeater=rrulestr_to_org(rule))
    obj._allow_short_range = allow_short_range
    return obj


def rrulestr_to_org(rrulestr: str) -> tuple[str, int, str] | None:
    """
    Converts an RRULE string to an org-mode repeater string.

    This function takes an RRULE string as input and returns a tuple
    representing an org-mode repeater string. If the RRULE string is not
    supported or cannot be converted, the function returns None.

    Args:
    ----
        rrulestr: The RRULE string to convert.


    Returns
    -------
        A tuple representing an org-mode repeater string, or None if the RRULE
        string is not supported or cannot be
        converted.

    """
    try:
        obj: rrule = rrulestr_to_rrule(rrulestr)
    except ValueError:
        return None
    else:
        if rrule_is_supported(obj):
            return _rrule_to_org(obj)
        else:
            return None


def _rrule_to_org(obj: rrule) -> tuple[str, int, str] | None:
    """
    Returns the original repeater string.

    Args:
    ----
        obj (rrule): An rrule object.

    Returns
    -------
        str: The original repeater string.
    """
    freq_map: tuple = ('y', 'm', 'w', 'h')
    interval: int = obj._interval
    frequency: str = freq_map[obj._freq]
    return '+', interval, frequency


def rrulestr_to_rrule(value: str) -> rrule:
    """
    Parses the RRULE text and returns an rrule object.

    Args:
    ----
        text (str): The RRULE text.

    Returns
    -------
        rrule: An rrule object.
    """
    obj: rrule | rruleset = rrulestr(value)
    if isinstance(obj, rruleset):
        raise ValueError('Only 1 RRULE supported')
    else:
        return obj


def rrulestr_is_supported(value: str) -> bool:
    """
    Check if an iCalendar recurrence rule string is supported.

    This function checks if a given iCalendar recurrence rule string is
    supported. An empty string is considered a supported rrule. The function
    parses the string to an rrule object and checks if it is supported.

    Args:
    ----
        value (str): The iCalendar recurrence rule string to check.

    Returns
    -------
        bool: True if the recurrence rule string is supported, False otherwise.

    Raises
    ------
        AssertionError: If `value` is not a str.
    """
    assert isinstance(value, str), '`value` must be a str'

    if not value:
        return True  # empty rrule is supported
    else:
        obj: rrule = rrulestr_to_rrule(value)
        return rrule_is_supported(obj)


def rrule_is_supported(rrule_obj: rrule,
                       max_days: int = MAX_WEEKDAYS,
                       unsupported: tuple = NOT_SUPPORTED) -> bool:
    """
    Check if a given rrule object is supported.

    This function checks if a given rrule object is supported. The rrule is
    considered unsupported if it has any of the attributes specified in
    `unsupported`. The rrule is also considered unsupported if it has more than
    `max_days` weekdays.

    Args:
    ----
        rrule_obj (rrule): The rrule object to check for support.
        max_days (int, optional): The maximum number of weekdays allowed.
        Defaults to MAX_WEEKDAYS.
        unsupported (tuple, optional): A tuple of strings representing
        unsupported attributes. Defaults to NOT_SUPPORTED.

    Returns
    -------
        bool: True if the rrule object is supported, False otherwise.
    """
    rrule_is_supported: bool = all(
        bool(getattr(rrule_obj, x, None)) is False
        for x in unsupported
    )

    if rrule_obj._byweekday is None:
        weekday_is_supported: bool = True
    else:
        weekday_is_supported: bool = len(rrule_obj._byweekday) < max_days

    return rrule_is_supported and weekday_is_supported
