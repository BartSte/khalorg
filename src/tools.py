from orgparse.date import OrgDate


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

    def __init__(self, heading: str, scheduled: OrgDate, deadline: OrgDate,
                 properties: dict, body: str):
        """

        Args:
        ----
            self (): 
            heading (str): 
            scheduled (OrgDate): 
            deadline (OrgDate): 
            properties (dict): 
            body (str): 
        """
        self.heading: str = heading
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

    @classmethod
    def compare(cls, a, b) -> bool:
        return all([getattr(a, x) == getattr(b, x) for x in vars(a)])
