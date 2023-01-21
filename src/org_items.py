import re
import sys

import orgparse
from orgparse.date import OrgDate
from orgparse.node import OrgNode


class OrgAgendaItemError(Exception):
    """Raised for an error in OrgAgendaItem."""


class NvimOrgDate(OrgDate):
    """
    OrgDate with a modified __str__ method.

    The class description of OrgDate contains the following:

    ````
    When formatting the date to string via __str__, and there is an end date on
    the same day as the start date, allow formatting in the short syntax
    <2021-09-03 Fri 16:01--17:30>? Otherwise the string represenation would be
    <2021-09-03 Fri 16:01>--<2021-09-03 Fri 17:30>
    ```

    However, the notation <2021-09-03 Fri 16:01--17:30> is not recognized by
    neovim's plugin nvim-orgmode. As a workaround, the following notation of a
    time interval is used in this specific case: <2021-09-03 Fri 16:01-17:30>.
    """

    day: str = '[A-Z]{1}[a-z]{2}'
    time: str = '[0-9]{2}:[0-9]{2}'
    date: str = '[0-9]{4}-[0-9]{2}-[0-9]{2}'
    regex: str = f'(<{date} {day} {time})--({time}>)'

    def __str__(self) -> str:
        date: str = super().__str__()
        return re.sub(self.regex, '\\1-\\2', date)


class OrgAgendaItem:
    """Represents an org agenda item.

    Attributes
    ----------
        heading: heading of the item.
        time_stamps: time stamp in org format.
        scheduled: time stamp that belongs to :SCHEDULED:
        deadline: time stamp that belongs to :DEADLINE:
        properties: a dict containing the :PROPERTIES:
        body: all text that is not part of PROPERTIES, DEADLINE, or SCHEDULED.
    """

    MESSAGE_INVALID_NODE: str = 'Invalid org node. No child node exists.'

    def __init__(self,
                 heading: str = '',
                 time_stamps: list[NvimOrgDate] = [],
                 scheduled: NvimOrgDate = NvimOrgDate(None),
                 deadline: NvimOrgDate = NvimOrgDate(None),
                 properties: dict = {},
                 body: str = ''):
        """Init.

        Args:
        ----
            heading: heading of the item.
            time_stamps: time stamp in org format.
            scheduled: time stamp that belongs to :SCHEDULED:
            deadline: time stamp that belongs to :DEADLINE:
            properties: a dict containing the :PROPERTIES:
            body: all text that is not part of PROPERTIES, DEADLINE,
            or SCHEDULED.
        """
        self.heading: str = heading
        self.time_stamps: list[OrgDate] = list(time_stamps)
        self.scheduled: NvimOrgDate = scheduled
        self.deadline: NvimOrgDate = deadline
        self.properties: dict = properties
        self.body: str = body

    def load_from_stdin(self) -> 'OrgAgendaItem':
        """Load an agenda item from stdin.

        Returns
        -------
            OrgAgendaItem: returns itself.
        """
        node: OrgNode = orgparse.loads(sys.stdin.read())
        return self.load_from_org_node(node)

    def load_from_org_node(self, node: OrgNode) -> 'OrgAgendaItem':
        """Load an agenda item from an `OrgNode`.

        Args:
            node: an org file that is parsed as `OrgNode`

        Returns
        -------
            OrgAgendaItem: returns itself.

        """
        child: OrgNode = self.get_child_node(node)
        kwargs: dict = dict(active=True, inactive=False, range=True, point=True)  # noqa
        time_stamps: list[OrgDate] = child.get_timestamps(**kwargs)

        self.body = child.body
        self.heading = child.heading
        self.deadline = NvimOrgDate(child.deadline.start, child.deadline.end)
        self.scheduled = NvimOrgDate(
            child.scheduled.start, child.scheduled.end)
        self.properties = child.properties
        self.time_stamps = [NvimOrgDate.list_from_str(str(x)).pop()
                            for x in time_stamps]

        return self

    def get_child_node(self, node: OrgNode) -> OrgNode:
        """The first child of the `node` is expected to be the agenda item.

        Args:
            node: the agenda item as `OrgNode`

        Returns
        -------
            OrgNode: the agenda item.

        """
        try:
            return node.root.children[0]
        except IndexError as error:
            raise OrgAgendaItemError(self.MESSAGE_INVALID_NODE) from error

    def __eq__(self, other) -> bool:
        try:
            return self.compare(self, other)
        except AttributeError as error:
            message: str = 'Try using a object of type OrgAgendaItem.'
            raise AttributeError(message) from error

    @staticmethod
    def compare(a: 'OrgAgendaItem', b:  'OrgAgendaItem') -> bool:
        """The equality of the `vars` of a and b should all be True.

        Args:
            a: agenda item 
            b: agenda item

        Returns:
            bool: True if the items are equal.
            
        """
        return all([getattr(a, x) == getattr(b, x) for x in vars(a)])
