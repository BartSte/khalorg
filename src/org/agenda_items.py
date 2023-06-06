import logging
from datetime import date, datetime
from typing import Generator

import orgparse
from orgparse.date import OrgDate
from orgparse.node import OrgNode

from src.helpers import get_khalorg_format
from src.org.helpers import get_indent, remove_timestamps
from src.rrule import rrulestr_is_supported, set_org_repeater

Time = date | datetime


class InvalidOrgItemError(Exception):
    """Raised for an error in OrgAgendaItem."""


class EmptyOrgItemError(Exception):
    """ The org agenda is empty. """


class OrgAgendaItem:
    """
    Represents 1 org agenda item that may consist of multiple OrgDate object,
    property field that can be accessed as dictionaries, and a heading and a
    body.

    Attributes
    ----------
        heading: heading of the item.
        time_stamps: time stamp in org format.
        properties: a dict containing the :PROPERTIES:
        body: all text that is not part of PROPERTIES
    """

    MESSAGE_INVALID_NODE: str = 'No agenda item was found.'

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
        self._timestamps: list[OrgDate] = []

        self.title: str = title
        self.timestamps = timestamps
        self.properties: dict = properties
        self.description: str = description

    @property
    def timestamps(self) -> list[OrgDate]:
        """
        Returns a list of OrgDate objects that are sorted by start date.

        Returns
        -------
            list of sorted org dates

        """
        return self._timestamps

    @timestamps.setter
    def timestamps(self, timestamps: list[OrgDate]):
        """
        Ensures the timestamps are sorted by start date, and the short range
        notation is disabled.

        Args:
        ----
            value: list of OrgDate objects
        """
        timestamps.sort(key=lambda x: x.start)
        for timestamp in timestamps:
            timestamp._allow_short_range = False

        self._timestamps = timestamps

    @property
    def first_timestamp(self) -> OrgDate:
        """
        Returns the first timestamp of a sorted list of OrgDate objects.

        Returns
        -------
            the OrgDate objects with the first start date.

        """
        try:

            return self.timestamps[0]
        except IndexError as error:
            message: str = 'Timestamp missing in agenda item'
            raise InvalidOrgItemError(message) from error

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
        kwargs: dict[str, bool] = dict(
            active=True,
            inactive=False,
            range=True,
            point=True)

        self.title = item.heading
        self.properties = item.properties
        self.timestamps = item.get_timestamps(**kwargs)
        self.description = remove_timestamps(item.body)

        return self

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
            raise EmptyOrgItemError(self.MESSAGE_INVALID_NODE) from error

    @property
    def until(self) -> OrgDate:
        """
        Return the UNTIL property as an OrgDate.

        If the OrgDateAgenda.first_timestamp has a time component, `until` must
        also have a time component. If this is not the case, add the time part
        of `datetime.min`.

        Returns
        -------
            end date of recurring items as an OrgDate

        """
        until: OrgDate = OrgDate.from_str(self.properties.get('UNTIL', ''))
        start: datetime | date = until.start
        has_time = isinstance(start, datetime)

        if not until or has_time == self.first_timestamp.has_time():
            return until
        elif has_time:
            return OrgDate((start.year, start.month, start.day))
        else:
            time: datetime = datetime.combine(start, datetime.min.time())
            return OrgDate(time)

    @classmethod
    def from_node(cls, node: OrgNode) -> 'OrgAgendaItem':
        """
        Constructs an OrgAgendaItem object from an OrgNode.

        Args:
        ----
            node:

        Returns:
        -------

        """
        obj = cls()
        return obj.load_from_org_node(node)

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

    def split_property(self, key: str, delimiter: str = ', ') -> list:
        """
        It is assumed that the value is stored as a str that is separated by a
        `delimiter`. This function splits this string into a list using the
        `delimiter`.

        Args:
        ----
            delimiter: str that separates attendees

        Returns:
        -------
            value split by `delimiter` and retuned as a list
        """
        value: str
        try:
            value = self.properties[key]
        except KeyError:
            return []
        else:
            return value.split(delimiter)

    def __str__(self) -> str:
        """
        Return the org item as a str.

        Returns
        -------

        """
        spec: str = get_khalorg_format()
        return format(self, spec)

    def __format__(self, spec: str) -> str:
        """
        By providing a `spec`, which is a template where values that are
        surrounded by curly-braces will be formatted. The following keys are
        avauilable:
            - attendees
            - calendar
            - categories
            - description
            - location
            - organizer
            - rrule
            - status
            - timestamps
            - title
            - uid
            - until
            - url.

        Using other keys will result in an error.

        Args:
        ----
            spec: a template where keys surrounded by "{}" will be formatted.

        Returns:
        -------
            the formatted `spec`

        """
        uid: str = str(self.properties.get('UID', ''))

        try:
            return spec.format(
                title=self.title,
                timestamps=self.get_timestamps_as_str(spec),
                attendees=self.properties.get('ATTENDEES', ''),
                calendar=self.properties.get('CALENDAR', ''),
                categories=self.properties.get('CATEGORIES', ''),
                uid=uid,
                location=self.properties.get('LOCATION', ''),
                organizer=self.properties.get('ORGANIZER', ''),
                rrule=self.properties.get('RRULE', ''),
                status=self.properties.get('STATUS', ''),
                url=self.properties.get('URL', ''),
                until=self.properties.get('UNTIL', ''),
                description=self.description)
        except KeyError as error:
            message: str = 'Unsupported key encountered in `spec`'
            raise KeyError(message) from error

    def get_timestamps_as_str(self, spec: str) -> str:
        """
        The timestamps are joined with a newline. To ensure a constant
        indent, the `get_indent` function is used.

        Args:
        ----
            spec: the used spec is needed to determine the indent.

        Returns:
        -------
            the indented timestamps

        """
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
    """
    An OrgAgendaFile object represents a collection of OrgAgendaItem objects
    that are stored at OrgAgendaFile.items.

    If the OrgAgendaItems contain an RRULE property, then the appropriate
    OrgDateAgenda objects can be determined and applied to the items using
    OrgAgendaFile.apply_rrules.

    The OrgAgendaFile objects can be formatted with a `spec` such that a
    formatted string can be returned. This is similar to the `khal list` command
    but for org items.

    Attributes
    ----------
        nodes: An OrgNode object representing the parsed org file.
        items: A list of OrgAgendaItem objects representing the agenda items.
    """

    def __init__(self, nodes: OrgNode) -> None:
        """
        Initializes a new instance of the OrgAgendaFile class.

        Args:
        ----
            nodes: An OrgNode object representing the parsed org file.

        Returns:
        -------
            None.
        """
        self.nodes: OrgNode = nodes
        self.items: list[OrgAgendaItem] = [OrgAgendaItem.from_node(x)
                                           for x in nodes if not x.is_root()]

    def apply_rrules(self) -> 'OrgAgendaFile':
        """
        Applies the RRULE properties of OrgAgendaItems to generate the appropriate
        OrgDateAgenda objects and applies them to the OrgAgendaItems.

        Returns
        -------
            An instance of the OrgAgendaFile class with updated items.
        """
        uids = set()
        items = []
        agenda_timestamps = OrgDateAgenda(self.nodes)

        for item in self.items:
            uid: str = item.properties['UID']
            if uid not in uids:
                item.timestamps = agenda_timestamps.dates[uid]
                item.properties['RRULE'] = agenda_timestamps.get_rrulestr(uid)
                uids.add(uid)
                items.append(item)

        self.items = items
        return self

    def __format__(self, spec: str) -> str:
        """
        Formats the OrgAgendaFile object with the given spec.

        Args:
        ----
            spec: A string containing the format specifier.

        Returns:
        -------
            A formatted string.
        """
        return '\n'.join(format(x, spec) for x in self.items)

    @ classmethod
    def from_str(cls, items: str) -> 'OrgAgendaFile':
        """
        Creates a new instance of the OrgAgendaFile class from a string
        representation of the org file.

        If `items` is an empty str it is replaced by '\n'

        Args:
        ----
            items: A string containing the org file.

        Returns:
        -------
            An instance of the OrgAgendaFile class.
        """
        items = items or '\n'
        return cls(orgparse.loads(items))


class OrgDateAgenda:
    """
    An object or this class groups all date together based on their UID value,
    by feeding it an OrgNode (python representation of an org file). For this,
    a value for the property "UID" is needed.

    Additionally, py providing an RRULE property, the appropriate org repeaters
    will be created.

    By calling OrgDateAgenda.as_str all OrgDate objects belonging to a UID wil
    be concatinated and separated by a newline. As such, 1 OrgAgendaItem can
    have multiple (recurring) OrgDate objects.

    Attributes
    ----------
        TIME_STAMPS_TYPES (dict): A dictionary defining the types of timestamps
            that can be processed by the class.
        dates (dict): A dictionary containing the dates associated with each UID.
        rrules (dict): A dictionary containing the recurrence rules associated
            with each UID.

    """

    TIME_STAMPS_TYPES: dict = dict(
        active=True,
        inactive=False,
        range=True,
        point=True
    )

    def __init__(self, nodes: OrgNode | None = None) -> None:
        """
        Initializes a new instance of the OrgDateAgenda class.

        Args:
        ----
            nodes (OrgNode | None): An OrgNode object or None. Defaults to None.

        Returns:
        -------
            None.
        """
        self.dates: dict[str, list[OrgDate]] = {}
        self.rrules: dict[str, set[str]] = {}
        self.unsupported_rrules: dict[str, set[str]] = {}
        if nodes:
            self.add_node(nodes)

    @classmethod
    def from_str(cls, org_file: str) -> 'OrgDateAgenda':
        """
        Creates a new instance of the OrgDateAgenda class from a string.

        Args:
        ----
            org_file (str): The Org file contents as a string.

        Returns:
        -------
            OrgDateAgenda: A new instance of the OrgDateAgenda class.
        """
        node: OrgNode = orgparse.loads(org_file)
        return cls(node)

    def add_node(self, nodes: OrgNode) -> None:
        """
        Adds nodes to the OrgDateAgenda object.

        Args:
        ----
            nodes (OrgNode): An OrgNode object.

        Returns:
        -------
            None.
        """
        agenda_items: Generator = (x for x in nodes if x.is_root() is False)

        for item in agenda_items:
            uid, timestamp, rule = self._parse_node(item)
            self.add(uid, timestamp, rule)

    def new(self, uid: str) -> None:
        """
        Creates a new UID in the OrgDateAgenda object.

        Args:
        ----
            uid (str): The UID to create.

        Returns:
        -------
            None.
        """
        self.rrules[uid] = set()
        self.unsupported_rrules[uid] = set()
        self.dates[uid] = []

    def add(self, uid: str, timestamp: OrgDate, rule: str) -> None:
        """
        Adds a date and/or recurrence rule to a UID in the OrgDateAgenda object.

        Args:
        ----
            uid (str): The UID to add the date and/or rule to.
            timestamp (OrgDate): The date to add.
            rule (str): The recurrence rule to add.

        Returns:
        -------
            None.
        """
        if uid not in self.uids:
            self.new(uid)

        supported_rule: bool = rrulestr_is_supported(rule)
        empty_rule: bool = bool(rule) is False
        new_rule: bool = all(rule != x for x in self.rrules[uid])
        new_timestamp: bool = all(timestamp != x for x in self.dates[uid])

        if (empty_rule and new_timestamp) or (new_rule and supported_rule):
            timestamp_with_repeater: OrgDate = set_org_repeater(timestamp, rule)  # noqa
            self.rrules[uid].add(rule)
            self.dates[uid].append(timestamp_with_repeater)
        elif new_rule and not supported_rule:
            self.dates[uid].append(timestamp)
            self.unsupported_rrules[uid].add(rule)

    @property
    def uids(self):
        """
        The UID value that exist in the agenda.

        Returns
        -------

        """
        return list(self.dates.keys())

    def _parse_node(
            self,
            node: OrgNode,
            allow_short_range: bool = False) -> tuple:
        """
        Returns the UID, the timestamp, and the RRULE from an OrgNode.

        Args:
        ----
            node: object that represents an org file
            allow_short_range: see OrgDate._allow_short_range

        Returns:
        -------
            the UID, timestamp, and RRULE property of an OrgNode.

        """
        uid: str = str(node.properties.get('UID', ''))
        rule: str = str(node.properties.get('RRULE', ''))
        timestamp: OrgDate = node.get_timestamps(**self.TIME_STAMPS_TYPES)[0]
        timestamp._allow_short_range = allow_short_range

        return uid, timestamp, rule

    def as_str(self, uid: str) -> str:
        """
        The agenda is returned as a str.

        Args:
        ----
            uid:  the UID

        Returns:
        -------
            item as a str
        """
        return '\n'.join([str(x) for x in self.dates[uid]])

    def get_rrulestr(self, uid: str) -> str:
        """
        Return the rrule that describes the recurrence of the OrgDateAgenda
        object, whether the rule is supported or not.

        Args:
        ----
            uid: the identifier of the rrule.

        Returns:
        -------
            the RRULE as a str

        """
        rules: set = self.rrules[uid] | self.unsupported_rrules[uid]
        return ';'.join([x for x in rules if x])
