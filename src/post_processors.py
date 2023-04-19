"""
Contains post processing functionality for adjusting the results of `khal`
commands.
"""

import logging
import re
from datetime import date, datetime
from typing import Callable, Generator

import orgparse
from dateutil.rrule import rrule, rruleset, rrulestr
from khal.khalendar import CalendarCollection
from orgparse.node import OrgNode
from src.helpers import substitude_with_placeholder

from src.khal_items import get_calendar_collection

_Time = date | datetime


def edit_attendees(
        calendar: str | CalendarCollection,  # type: ignore
        attendees: tuple | list,
        summary: str,
        start: _Time,
        end: _Time) -> None:
    """
    For `calendar` the `attendees` are added to all events that adhere to
    the `summary`, the `start` time, and the `stop` time.

    When `calendar` is a CalendarCollection the step of searching for a
    calendar collection can be omitted.

    Args:
    ----
        calendar: the calendar name or a CalendarCollection object.
        attendees: list of attendees
        summary: search query. The summary/title of the event is recommended.
        start: start of the event.
        end: end of the event.
    """
    if isinstance(calendar, str):
        calendar: CalendarCollection = get_calendar_collection(calendar)

    logging.debug(f'Get events on date: {start}')
    events: Generator = (
        x for x in calendar.get_events_on(start)
        if x.summary == summary and _replace(x.end, tzinfo=None) == end
    )

    for event in events:
        event.update_attendees(attendees)
        calendar.update(event)
        logging.info(f'Event: {event.summary} was updated')


def _replace(obj: _Time, **kwargs) -> _Time:
    try:
        return obj.replace(**kwargs)
    except (AttributeError, TypeError):
        return obj

class RegexReply:
    """
    A class that defines a regular expression reply object.

    Attributes:
        freq_map (tuple): A tuple of frequency codes.
        rrule_unsupported (tuple): A tuple of unsupported RRULE attributes.

    Methods:
        __call__(self, match: re.Match) -> str:
            The main method that returns the original repeater after parsing the
            RRULE.

        get_rrule(self, text: str) -> rrule:
            Parses the RRULE text and returns an rrule object.

        get_org_repeater(self, obj: rrule) -> str:
            Returns the original repeater string.

        _get_org_repeater(self, obj: rrule) -> str:
            Returns the original repeater string.

        is_supported(self, obj: rrule) -> bool:
            Checks whether the RRULE is supported.

        _is_rrule_supported(self, obj: rrule) -> bool:
            Checks whether the RRULE attributes are supported.

        _is_byweekday_supported(self, repeater: rrule) -> bool:
            Checks whether the BYWEEKDAY attribute is supported.
    """

    freq_map: tuple = ('y', 'm', 'w', 'h')
    rrule_unsupported = ('_byeaster', '_bymonthday', '_bynmonthday', '_bynweekday',
                         '_bysetpos', '_byweekno', '_byyearday')

    def __call__(self, match: re.Match) -> str:
        """
        Parses the RRULE and returns the original repeater.

        Args:
            match (re.Match): The regular expression match object.

        Returns:
            str: The original repeater string.
        """
        try:
            repeater: rrule = self.get_rrule(match.group('content'))
        except ValueError:
            return ''
        else:
            return self.get_org_repeater(repeater)

    def get_rrule(self, text: str) -> rrule:
        """
        Parses the RRULE text and returns an rrule object.

        Args:
            text (str): The RRULE text.

        Returns:
            rrule: An rrule object.
        """
        obj: rrule | rruleset = rrulestr(text)
        if isinstance(obj, rruleset):
            raise ValueError('Only 1 RRULE supported')
        else:
            return obj

    def get_org_repeater(self, obj: rrule) -> str:
        """
        Returns the original repeater string.

        Args:
            obj (rrule): An rrule object.

        Returns:
            str: The original repeater string.
        """
        if self.is_supported(obj):
            return self._get_org_repeater(obj)
        else:
            return ''

    def _get_org_repeater(self, obj: rrule) -> str:
        """
        Returns the original repeater string.

        Args:
            obj (rrule): An rrule object.

        Returns:
            str: The original repeater string.
        """
        interval: int = obj._interval
        freq: str = self.freq_map[obj._freq]
        return f' +{interval}{freq}'

    def is_supported(self, obj: rrule) -> bool:
        """
        Checks whether the RRULE is supported.

        Args:
            obj (rrule): An rrule object.

        Returns:
            bool: True if the RRULE is supported, False otherwise.
        """
        return self._is_rrule_supported(obj) and self._is_byweekday_supported(obj)
        
    def _is_rrule_supported(self, obj: rrule) -> bool:
        return all(bool(getattr(obj, x, None)) is False for x in self.rrule_unsupported)

    def _is_byweekday_supported(self, repeater: rrule) -> bool:
        return len(repeater._byweekday) < 2


class ListPostProcessor:
    """
    `khalorg list` relies on the command: `khal list`.

    The following items need to be removed:
    - Duplicates: same uid and timestamp
    - Recurring items: same uid and timestamp has a repeat pattern

    Attributes
    ----------
        timestamp_kwargs: the timestamp type that is requested. See
        orgparse.OrgNode.
    """

    _TIME_STAMPS_KWARGS: dict = dict(
        active=True,
        inactive=False,
        range=True,
        point=True
    )

    def __init__(self,
                 org_nodes: OrgNode,
                 time_stamps_kwargs: dict = _TIME_STAMPS_KWARGS) -> None:
        """
        Init.

        Args:
        ----
            org_items: a list of org nodes
            time_stamps_kwargs: timestamp type. See orgpare.OrgNode
        """
        self._ids: list
        self._timestamps: list
        self._unique_items: list

        self.nodes: OrgNode = org_nodes
        self.timestamp_kwargs: dict = time_stamps_kwargs

    def remove_duplicates(self) -> str:
        """
        Removes duplicated OrgNode objects.

        The results is also stored internally at PostProcessor.unique_items. An
        item is unique if the ics UID and the timestamps are unique. Recurring
        khal items have the same UID but different timestamps.

        Returns
        -------
            the unique OrgNode objects

        """
        self._reset()
        for item in self.nodes:

            new_id: str = str(item.properties.get('ID'))
            new_timestamp: list = item.get_timestamps(**self.timestamp_kwargs)

            if not self._exists(new_id, new_timestamp):
                self._append(item, new_id, new_timestamp)

        return self.unique_items

    def _reset(self):
        self._ids = []
        self._timestamps = []
        self._unique_items = []

    def _append(self, item: OrgNode, id: str, timestamp: list):
        self._ids.append(id)
        self._timestamps.append(timestamp)
        self._unique_items.append(str(item))

    def _exists(self, id: str, timestamp: list) -> bool:
        # 1 timestamp supported for now
        recurring: bool = id in self._ids and timestamp[0]._repeater
        duplicate: bool = id in self._ids and timestamp in self._timestamps
        return recurring or duplicate

    @property
    def unique_items(self) -> str:
        """
        Unique PostProcessor.nodes objects as a concatenated string.

        Returns
        -------
           a str with unique items

        """
        return '\n'.join(self._unique_items)

    @classmethod
    def from_str(cls, org_items: str) -> 'ListPostProcessor':
        nodes: OrgNode = orgparse.loads(org_items)
        return cls(nodes)
