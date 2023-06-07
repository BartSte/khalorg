import logging
from datetime import date, datetime
from enum import Enum, auto
from typing import Callable

from khalorg.khal.calendar import Calendar
from khalorg.khal.helpers import is_future as is_in_future
from khalorg.org.agenda_items import OrgAgendaItem
from khalorg.rrule import get_rrulestr, rrulestr_is_supported

Time = date | datetime


class EventChecks(Enum):
    """Checks that can be performed by EventChecker."""

    UID = auto()
    RRULE = auto()
    FUTURE = auto()
    DUPLICATE = auto()


class EventChecker:
    """
    Used to perform a set of checks before one of the Calendar commands are
    executed.
    """

    MESSAGE_RRULE: str = 'Org repeater not supported.'
    MESSAGE_FUTURE: str = 'Agenda item date not in the future.'
    MESSAGE_DUPLICATE: str = 'Agenda item already exists.'
    MESSAGE_UID: str = 'Agenda item its UID property is empty.'

    def __init__(self, checks: list[EventChecks] = [x for x in EventChecks]):
        """
        Init.

        Args:
        ----
            checks: Checks to perform. By default, all EventChecks are done.
        """
        self._enum_vs_func: dict = {
            EventChecks.DUPLICATE: self.is_duplicate,
            EventChecks.FUTURE: self.is_future,
            EventChecks.RRULE: self.valid_rrule,
            EventChecks.UID: self.has_uid
        }

        self.checks: list[EventChecks] = checks

    def remove(self, check: EventChecks):
        """
        Remove a EventChecks item from EventChecker.checks. A ValueError is
        catched if `check` is not in EventChecker.checks.

        Args:
        ----
            check: an EventChecks enum.
        """
        try:
            self.checks.remove(check)
        except ValueError:
            logging.info(f'{check} was not found in EventChecker.checks')

    def is_valid(self, calendar: str | Calendar, item: OrgAgendaItem) -> str:
        """
        Check if the `item` can be created in calendar `name`.

        Args:
        ----
            calendar: name of the Khal calendar or a Calendar object
            item: OrgAgendaItem object

        Returns:
        -------
            True if the item is not a duplicate and exists in the future, else
            return False
        """
        if isinstance(calendar, str):
            calendar = Calendar(calendar)

        messages: list = []

        kwargs: dict = dict(item=item, calendar=calendar)
        for check in self.checks:
            func: Callable = self._enum_vs_func[check]
            args = (kwargs.get(x) for x in func.__code__.co_varnames)
            args = [x for x in args if x is not None]
            messages.append(func(*args))

        messages = [x for x in messages if x]
        return '\n'.join(messages) if messages else ''

    def is_future(self, item: OrgAgendaItem) -> str:
        """
        Return an error message if the `item` is in the past.

        Args:
        ----
            item: OrgAgendaItem object

        Returns:
        -------
            empty str if the `item` is in the future, else a error message is
            returned.
        """
        future: bool = is_in_future(item.first_timestamp.start)
        return self.MESSAGE_FUTURE if not future else ''

    def is_duplicate(self, item: OrgAgendaItem, calendar: Calendar) -> str:
        """
        Return an error message if the `item` exists in `calendar`.

        Args:
        ----
            item: OrgAgendaItem object

        Returns:
        -------
            empty str if the `item` exists in `calendar`, else a error message
            is returned.
        """
        is_duplicate: bool = calendar.exists(
            item.title,
            item.first_timestamp.start,
            item.first_timestamp.end
        )
        return self.MESSAGE_DUPLICATE if is_duplicate else ''

    def valid_rrule(self, item: OrgAgendaItem) -> str:
        """
        Return an error message if the `item` contains an unsupportd RRULE.

        Args:
        ----
            item: OrgAgendaItem object

        Returns:
        -------
            empty str if the `item` contains an unsupported RRULE, else a error
            message is returned.
        """
        rule: str = get_rrulestr(
            item.first_timestamp.start,
            item.first_timestamp._repeater,
            item.until.start)

        valid_rrule: bool = rrulestr_is_supported(rule)
        return self.MESSAGE_RRULE if not valid_rrule else ''

    def has_uid(self, item: OrgAgendaItem) -> str:
        """
        Returns an error messages when the event has no UID.

        Args:
        ----
            item: the agenda item

        Returns:
        -------
            an error messages or an empty str.

        """
        return self.MESSAGE_UID if not item.properties.get('UID') else ''
