from orgparse.date import OrgDate
from orgparse.node import OrgNode


class OrgAgendaItem:

    def __init__(self,
                 heading: str,
                 time_stamps: list,
                 scheduled: OrgDate = OrgDate(None),
                 deadline: OrgDate = OrgDate(None),
                 properties: dict = {},
                 body: str = ''):

        self.heading: str = heading
        self.time_stamps: list = time_stamps
        self.scheduled: OrgDate = scheduled
        self.deadline: OrgDate = deadline
        self.properties: dict = properties
        self.body: str = body

    def __eq__(self, other) -> bool:
        try:
            return self.compare(self, other)
        except AttributeError as error:
            message: str = 'Try using a object of type OrgAgendaItem.'
            raise AttributeError(message) from error

    @staticmethod
    def compare(a, b) -> bool:
        return all([getattr(a, x) == getattr(b, x) for x in vars(a)])

    @classmethod
    def from_org_node(cls, node: OrgNode) -> 'OrgAgendaItem':
        child: OrgNode = node.root.children[0]

        kwargs: dict = dict(active=True, inactive=False, range=True, point=True)
        time_stamps: list = child.get_timestamps(**kwargs)

        return cls(
            child.heading,
            time_stamps=time_stamps,
            scheduled=OrgDate(child.scheduled.start, child.scheduled.end),
            deadline=OrgDate(child.deadline.start, child.deadline.end),
            properties=child.properties,
            body=child.body
        )
