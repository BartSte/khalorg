"""Containing workarounds for the interface to khal."""

import logging
from datetime import date, datetime
from typing import Generator

from khal.khalendar import CalendarCollection

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
