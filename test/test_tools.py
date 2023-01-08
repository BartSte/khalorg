from datetime import datetime
from unittest import TestCase

from orgparse.date import OrgDate
from src.tools import OrgAgendaItem


class TestOrgAgendaItem(TestCase):

    """ TODO """
    def test_eq(self):
        """TODO

        Args:
            self (): 
        """
        heading: str = 'test'
        scheduled: OrgDate = OrgDate(datetime(2023, 1, 1),
                                     datetime(2023, 1, 2))
        deadline: OrgDate = OrgDate(datetime(2023, 1, 1),
                                    datetime(2023, 1, 2))
        properties: dict = {'ID': '123',
                            'CALENDAR': 'outlook',
                            "LOCATION": 'Somewhere',
                            "ORGANIZER":  'Someone (someone@outlook.com)'}
        body: str = 'test'

        a = OrgAgendaItem(heading, scheduled, deadline, properties, body)
        b = OrgAgendaItem(heading, scheduled, deadline, properties, body)
        c = OrgAgendaItem('xxxxx', scheduled, deadline, properties, body)
        d = OrgAgendaItem(heading, '', deadline, properties, body)
        e = OrgAgendaItem(heading, scheduled, '', properties, body)
        f = OrgAgendaItem(heading, scheduled, deadline, {}, body)
        g = OrgAgendaItem(heading, scheduled, deadline, properties, '')

        self.assertTrue(a == b)
        self.assertFalse(a == c)
        self.assertFalse(a == d)
        self.assertFalse(a == e)
        self.assertFalse(a == f)
        self.assertFalse(a == g)
