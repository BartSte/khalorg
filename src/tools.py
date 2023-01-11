import logging

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

    def __init__(self,
                 heading: str,
                 time_stamp: OrgDate = OrgDate(None),
                 scheduled: OrgDate = OrgDate(None),
                 deadline: OrgDate = OrgDate(None),
                 properties: dict = {},
                 body: str = ''):
        """

        Args:
            self (): 
            heading (str): 
            time_stamp (OrgDate): 
            scheduled (OrgDate): 
            deadline (OrgDate): 
            properties (dict): 
            body (str): 
        """
        # TODO, only 1 date is parsed py the orgparse, the one that is on top.
        # the rest is placed in the body of the message. The dates are gathered
        # in a variable called: datelist
        self.heading: str = heading
        self.time_stamps: OrgDate = time_stamp
        self.scheduled: OrgDate = scheduled
        self.deadline: OrgDate = deadline
        self.properties: dict = properties
        self.body: str = body

        assert self.has_date, self.error_no_date
        logging.debug(f'date_is_provided: {self.has_date}')

    @property
    def has_date(self) -> bool:
        """TODO.

        Args:
            self ():

        Returns
        -------

        """
        return bool(self.time_stamps or self.scheduled or self.deadline)

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
        """

        Args:
            cls ():
            node (OrgNode):

        Returns
        -------

        """
        child: OrgNode = node.root.children[0]
        return cls(
            child.heading,
            time_stamp=OrgDate(child.datelist[0]),
            scheduled=OrgDate(child.scheduled.start, child.scheduled.end),
            deadline=OrgDate(child.deadline.start, child.deadline.end),
            properties=child.properties,
            body=child.body
        )
