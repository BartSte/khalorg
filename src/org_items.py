import sys

import orgparse
from orgparse.date import OrgDate
from orgparse.node import OrgNode


class OrgAgendaItemError(Exception):
    """
    Todo.:
    ----.
    """


class OrgAgendaItem:

    MESSAGE_INVALID_NODE: str = 'Invalid org node. No child node exists.'

    def __init__(self,
                 heading: str = '',
                 time_stamps: list = [],
                 scheduled: OrgDate = OrgDate(None),
                 deadline: OrgDate = OrgDate(None),
                 properties: dict = {},
                 body: str = ''):

        self.heading: str = heading
        self.time_stamps: list = list(time_stamps)
        self.scheduled: OrgDate = scheduled
        self.deadline: OrgDate = deadline
        self.properties: dict = properties
        self.body: str = body

    def load_from_stdin(self) -> 'OrgAgendaItem':
        node: OrgNode = orgparse.loads(sys.stdin.read())
        return self.load_from_org_node(node)

    def load_from_org_node(self, node: OrgNode) -> 'OrgAgendaItem':
        child: OrgNode = self.get_child_node(node)
        time_stamps: list = child.get_timestamps(active=True, inactive=False,
                                                 range=True, point=True)

        self.body = child.body
        self.heading = child.heading
        self.deadline = OrgDate(child.deadline.start, child.deadline.end)
        self.scheduled = OrgDate(child.scheduled.start, child.scheduled.end)
        self.properties = child.properties
        self.time_stamps = time_stamps

        return self

    def get_child_node(self, node: OrgNode) -> OrgNode:
        """TODO.

        Args:
            node:

        Returns
        -------

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
    def compare(a, b) -> bool:
        return all([getattr(a, x) == getattr(b, x) for x in vars(a)])
