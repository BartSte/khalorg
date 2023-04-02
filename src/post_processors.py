"""
Contains post processing functionality for adjusting the results of `khal`
commands.
"""
from typing import Iterable

from khal.cli import build_collection
from khal.khalendar import CalendarCollection
from khal.khalendar.khalendar import Event
from khal.settings.settings import find_configuration_file, get_config
from orgparse.node import OrgNode


class Attendees:

    """Update the Attendees field in a Khal Event loading the Khal calendar.

    TODO write a test for this.
    """
    def __init__(self, calendar_name: str, event_query: str):
        self._query: str = event_query
        self._event: Iterable[Event]
        self._config: dict
        self._calendar: CalendarCollection

        self.path_config: str | None = find_configuration_file()
        self.calendar_name: str = calendar_name

    def load(self):
        self._config = get_config(self.path_config)
        self._calendar = build_collection(self._config, self.calendar_name)
        self._events = self._calendar.search(self._query)

    def update(self, attendees: list):
        for event in self._events:
            event.update_attendees(attendees)
            self._calendar.update(event)


class Export:
    """
    `khalorg export` relies on the command: `khal --format`. This command
    duplicates multi-day items. This PostProcessor class aims to remove such
    duplicates.

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
        return id in self._ids and timestamp in self._timestamps

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
    def from_str(cls, org_items: str) -> 'Export':
        nodes: OrgNode = orgparse.loads(org_items)
        return cls(nodes)
