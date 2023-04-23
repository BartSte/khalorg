from dateutil.rrule import rrule, rruleset, rrulestr
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


def get_orgdate(
        date: OrgDate,
        rule: str,
        allow_short_range: bool = False) -> OrgDate:
    obj: OrgDate = OrgDate(
        start=date.start,
        end=date.end,
        active=True,
        repeater=rrulestr_to_org(rule))
    obj._allow_short_range = allow_short_range
    return obj


def rrulestr_to_org(rrulestr: str) -> tuple[str, int, str] | None:
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
    Todo:
    ----
    ----.

    Args:
    ----
        value:

    Returns
    -------

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
    TODO.

    Args:
    ----
        obj:

    Returns
    -------

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
