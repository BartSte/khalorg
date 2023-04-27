import logging
import re
import sys
from dataclasses import dataclass
from typing import Generator

import orgparse
from orgparse.date import OrgDate
from orgparse.node import OrgNode

from src.helpers import get_indent
from src.rrule import get_orgdate, rrulestr_is_supported


class OrgAgendaItemError(Exception):
    """Raised for an error in OrgAgendaItem."""


def remove_timestamps(body: str) -> str:
    """
    OrgNode.body contains the time_stamps that should be removed because the
    time stamps are already parsed in OrgAgendaItem.time_stamps and
    will otherwise be duplicated.

    If a line only contains a time stamp and spaces, the whole line is
    deleted. If it is surrounded by characters, it is only removed.

    Args:
    ----
        body: str containing time stamps
        time_stamps: list of NvimOrgDate objects

    Returns:
    -------

    """
    result: str = body
    regex: str = f'(^[ ]*{OrgRegex.timestamp_long}[ ]*[\n]*)'
    regex += f'|({OrgRegex.timestamp_long})'
    result: str = re.sub(regex, '', result, re.M)

    # Remove indent first line.
    result = re.sub(r'^\s+', '', result, re.MULTILINE)

    return result


@dataclass
class OrgRegex:
    day: str = '[A-Z]{1}[a-z]{2}'
    time: str = '[0-9]{2}:[0-9]{2}'
    date: str = '[0-9]{4}-[0-9]{2}-[0-9]{2}'
    repeater: str = '[-+]{1,2}[0-9]+[a-z]+'
    timestamp: str = f'<{date}( {day})?( {time})?( {repeater})?>'
    timestamp_short: str = f'(<{date} {day} {time})--({time} ({repeater})?>)'
    timestamp_long: str = f'{timestamp}--{timestamp}'


class OrgDateAgenda:
    TIME_STAMPS_TYPES: dict = dict(
        active=True,
        inactive=False,
        range=True,
        point=True
    )

    def __init__(self, nodes: OrgNode | None = None) -> None:
        self.dates: dict[str, list[OrgDate]] = {}
        self.rrules: dict[str, set[str]] = {}
        if nodes:
            self.add_node(nodes)

    @classmethod
    def from_str(cls, org_file: str) -> 'OrgDateAgenda':
        node: OrgNode = orgparse.loads(org_file)
        return cls(node)

    def add_node(self, nodes: OrgNode) -> None:
        agenda_items: Generator = (x for x in nodes if x.is_root() is False)

        for item in agenda_items:
            uid, timestamp, rule = self._parse_node(item)
            self.add(uid, timestamp, rule)

    def new(self, uid: str):
        self.rrules[uid] = set()
        self.dates[uid] = []

    def add(self, uid: str, timestamp: OrgDate, rule: str):

        if uid not in self.uids:
            self.new(uid)

        supported_rule: bool = rrulestr_is_supported(rule)
        empty_rule: bool = bool(rule) is False
        new_rule: bool = all(rule != x for x in self.rrules[uid])
        new_timestamp: bool = all(timestamp != x for x in self.dates[uid])

        if (empty_rule and new_timestamp) or (new_rule and supported_rule):
            self.rrules[uid].add(rule)
            self.dates[uid].append(get_orgdate(timestamp, rule))
        elif new_rule and not supported_rule:
            self.dates[uid].append(timestamp)

    @property
    def uids(self):
        return list(self.dates.keys())

    def _parse_node(
            self,
            node: OrgNode,
            allow_short_range: bool = False) -> tuple:

        uid: str = str(node.properties.get('UID', ''))
        rule: str = str(node.properties.get('RRULE', ''))
        org_date: OrgDate = node.get_timestamps(**self.TIME_STAMPS_TYPES)[0]
        org_date._allow_short_range = allow_short_range

        return uid, org_date, rule

    def as_str(self, uid: str) -> str:
        return '\n'.join([str(x) for x in self.dates[uid]])


class OrgAgendaItem:
    """
    Represents an org agenda item.

    Attributes
    ----------
        heading: heading of the item.
        time_stamps: time stamp in org format.
        properties: a dict containing the :PROPERTIES:
        body: all text that is not part of PROPERTIES
    """

    MESSAGE_INVALID_NODE: str = 'Invalid org node. No child node exists.'

    def __init__(self,
                 title: str = '',
                 timestamps: list[OrgDate] = [],
                 properties: dict = {},
                 description: str = ''):
        """
        Init.

        Args:
        ----
            heading: heading of the item.
            time_stamps: time stamp in org format.
            properties: a dict containing the :PROPERTIES:
            body: all text that is not part of PROPERTIES
        """
        self.title: str = title
        self.timestamps: list[OrgDate] = timestamps
        self.properties: dict = properties
        self.description: str = description

    def load_from_stdin(self) -> 'OrgAgendaItem':
        """
        Load an agenda item from stdin.

        Returns
        -------
            OrgAgendaItem: returns itself.
        """
        return self.load_from_str(sys.stdin.read())

    def load_from_str(self, text: str) -> 'OrgAgendaItem':
        """
        Loads an agenda item from a str.

        Args:
        ----
            text: org agenda item as a str

        Returns:
        -------
            the agenda item

        """
        node: OrgNode = orgparse.loads(text)
        return self.load_from_org_node(node)

    def load_from_org_node(self, node: OrgNode) -> 'OrgAgendaItem':
        """
        Load an agenda item from an `OrgNode`.

        Args:
        ----
            node: an org file that is parsed as `OrgNode`

        Returns:
        -------
            OrgAgendaItem: returns itself.

        """
        item: OrgNode = self.get_first_agenda_item(node)
        kwargs: dict = dict(active=True, inactive=False, range=True, point=True)  # noqa

        self.title = item.heading
        self.properties = item.properties
        self.timestamps = item.get_timestamps(**kwargs)
        self.description = remove_timestamps(item.body)

        return self

    @classmethod
    def from_node(cls, node: OrgNode) -> 'OrgAgendaItem':
        obj = cls()
        return obj.load_from_org_node(node)

    def get_first_agenda_item(self, node: OrgNode) -> OrgNode:
        """
        The first non-root node is expected to be the agenda item.

        Args:
        ----
            node: the agenda item as `OrgNode`

        Returns:
        -------
            OrgNode: the agenda item.

        """
        items: list = [x for x in node if not x.is_root()]
        try:
            return items[0]
        except IndexError as error:
            raise OrgAgendaItemError(self.MESSAGE_INVALID_NODE) from error

    def __eq__(self, other) -> bool:
        try:
            return self.compare(self, other)
        except AttributeError as error:
            message: str = 'Try using a object of type OrgAgendaItem.'
            raise AttributeError(message) from error

    @staticmethod
    def compare(a: 'OrgAgendaItem', b: 'OrgAgendaItem') -> bool:
        """
        The equality of the `vars` of a and b should all be True.

        Args:
        ----
            a: agenda item
            b: agenda item

        Returns:
        -------
            bool: True if the items are equal.

        """
        attribute_equal: bool = all(
            getattr(a, x) == getattr(b, x) for x in vars(a).keys()
        )
        time_stamps_equal: bool = str(a.timestamps) == str(b.timestamps)
        return attribute_equal and time_stamps_equal

    def get_attendees(self, delimiter: str = ', ') -> list:
        """
        The attendees are stored as a str that is separated by a
        `delimiter`. This function splits this string into a list using the
        `delimiter`.

        Args:
        ----
            delimiter: str that separates attendees

        Returns:
        -------
            attendees as list
        """
        attendees: str
        try:
            attendees = self.properties['ATTENDEES']
        except KeyError:
            return []
        else:
            return attendees.split(delimiter)

    def __format__(self, spec: str) -> str:
        uid: str = str(self.properties['UID'])

        return spec.format(
            title=self.title,
            timestamps=self.get_timestamps_as_str(spec),
            attendees=self.properties['ATTENDEES'],
            calendar=self.properties['CALENDAR'],
            categories=self.properties['CATEGORIES'],
            uid=uid,
            location=self.properties['LOCATION'],
            organizer=self.properties['ORGANIZER'],
            rrule=self.properties['RRULE'],
            status=self.properties['STATUS'],
            url=self.properties['URL'],
            description=self.description)

    def get_timestamps_as_str(self, spec: str) -> str:
        timestamp_indents: list = get_indent(spec, '{timestamps}')
        generator: Generator = (str(x) for x in self.timestamps)

        if len(timestamp_indents) > 1:
            logging.warning('Only 1 timestamp indent is supported. First '
                            'indent found is used.')

        try:
            space = timestamp_indents[0]
        except IndexError:
            return '\n'.join(generator)
        else:
            return f'\n{space}'.join(generator)


class OrgAgendaFile:

    def __init__(self, nodes: OrgNode) -> None:
        self.nodes: OrgNode = nodes
        self.items: list[OrgAgendaItem] = [OrgAgendaItem.from_node(x)
                                           for x in nodes if not x.is_root()]

    def apply_rrules(self) -> 'OrgAgendaFile':
        uids = set()
        items = []
        with_repeaters = OrgDateAgenda(self.nodes)
        for item in self.items:
            uid: str = item.properties['UID']

            if uid not in uids:
                item.timestamps = with_repeaters.dates[uid]

                uids.add(uid)
                items.append(item)

        self.items = items
        return self

    def __format__(self, spec: str) -> str:
        return '\n'.join(format(x, spec) for x in self.items)

    @classmethod
    def from_str(cls, items: str) -> 'OrgAgendaFile':
        nodes: OrgNode = orgparse.loads(items)
        return cls(nodes)

