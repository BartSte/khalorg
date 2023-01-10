import logging
from typing import Union

from orgparse.date import OrgDate
from orgparse.node import OrgNode


class OrgAgendaItem:
    """

    Attributes
    ----------
        heading:
        scheduled:
        deadline:
        properties:
        body:
    """

    error_no_date: str = (
        'An OrgAgendaItem at least needs a `scheduled` date or a `deadline` '
        'date.'
    )

    def __init__(self, heading: str,
                 scheduled: Union[OrgDate, None] = None,
                 deadline: Union[OrgDate, None] = None,
                 properties: dict = {},
                 body: str = ''):
        """

        Args:
        ----
            heading (str):
            scheduled (Union[OrgDate, None]):
            deadline (Union[OrgDate, None]):
            properties (dict):
            body (str):
        """
        self.heading: str = heading
        self.scheduled: Union[OrgDate, None] = scheduled
        self.deadline: Union[OrgDate, None] = deadline
        self.properties: dict = properties
        self.body: str = body

        assert self.date_is_provided, self.error_no_date
        logging.debug(f'date_is_provided: {self.date_is_provided}')
        logging.debug(f'scheduled date is: {self.scheduled}')
        logging.debug(f'deadline date is: {self.deadline}')

    @property
    def date_is_provided(self) -> bool:
        """TODO.

        Args:
            self ():

        Returns
        -------

        """
        return any(isinstance(x, OrgDate)
                   for x in [self.scheduled, self.deadline])

    def __eq__(self, other) -> bool:
        """TODO.

        Args:
            self ():
            other ():

        Returns
        -------

        """
        try:
            return self.compare(self, other)
        except AttributeError as error:
            message: str = 'Try using a object of type OrgAgendaItem.'
            raise AttributeError(message) from error

    @staticmethod
    def compare(a, b) -> bool:
        """TODO.

        Args:
            a ():
            b ():

        Returns
        -------

        """
        return all([getattr(a, x) == getattr(b, x) for x in vars(a)])

    @classmethod
    def from_org_node(cls, node: OrgNode) -> 'OrgAgendaItem':

        child: OrgNode = node.children[0]
        return cls(
            child.heading,
            scheduled=OrgDate(child.scheduled.start, child.scheduled.end),
            deadline=OrgDate(child.deadline.start, child.deadline.end),
            properties=child.properties,
            body=child.body
        )
