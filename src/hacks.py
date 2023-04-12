"""Containing workarounds for the interface to khal."""

import logging
from datetime import date, datetime
from typing import Any

from khal.khalendar import CalendarCollection
from khal.khalendar.khalendar import Event

from src.khal_items import get_calendar_collection


def edit_attendees(
        calendar: str | CalendarCollection,  # type: ignore
        attendees: tuple | list,
        query: str,
        timestamp_start: datetime | date,
        timestamp_end: datetime | date) -> list:
    """
    For `calendar` the `attendees` are added to all events that adhere to
    the `query` and the start and stop times.

    When `calendar` is a CalendarCollection the step of searching for a
    calendar collection can be omitted.

    Args:
        calendar: the calendar name or a CalendarCollection object.
        attendees: list of attendees
        query: search query. The summary/title of the event is recommended.
        timestamp_start: start of the event.
        timestamp_end: end of the event.

    Returns
    -------
        the events that are edited.

    """

    if isinstance(calendar, str):
        calendar: CalendarCollection = get_calendar_collection(calendar)

    events: list[Event] = list(calendar.search(query))
    kwargs: dict = dict(tzinfo=None, microsecond=0)
    for event in events:

        start = _try_datetime_replace(event.start, **kwargs)
        end = _try_datetime_replace(event.end, **kwargs)

        if timestamp_start == start and timestamp_end == end:
            event.update_attendees(attendees)
            calendar.update(event)
            logging.info(f'Event: {event.summary} was updated')

    return events


def _try_datetime_replace(
        timestamp: datetime | date,
        **kwargs) -> datetime | date:
    try:
        return timestamp.replace(**kwargs)
    except TypeError:
        return timestamp
