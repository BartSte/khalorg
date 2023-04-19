"""
Contains post processing functionality for adjusting the results of `khal`
commands.
"""

import logging
import re
from datetime import date, datetime
from typing import Generator

import orgparse
from khal.khalendar import CalendarCollection
from orgparse.node import OrgNode

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


def convert_repeat_pattern(org_items: str) -> str:
    """
    TODO.

    Args:
        org_items:

    Returns
    -------

    """
    regex: str = (
        '(?P<head><[^>]*)'

        'FREQ=(?P<freq>[A-Z])[A-Z]*;'
        '(UNTIL=[A-Z0-9,]*;?)?'
        'INTERVAL=(?P<interval>[0-9]*);'
        '(?P<byday>BYDAY=[A-Z0-9,]*;?)?'
        '(WKST=[A-Z]*;?)?'

        '(?P<tail>[^<]*>)'
    )

    def replace(match: re.Match) -> str:
        head: str = match.group('head')
        tail: str = match.group('tail')
        freq: str = match.group('freq').lower()
        byday: str = match.group('byday')
        interval: str = match.group('interval')

        if re.match('.*[0-9,].*', byday): # unsupported for now
            return f'{head}{tail}'
        else:
            return f'{head} +{interval}{freq}{tail}'

    return re.sub(regex, replace, org_items)


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
