from datetime import datetime
from unittest import TestCase

from orgparse.date import OrgDate

from src.tools import OrgAgendaItem


class TestOrgAgendaItem(TestCase):
    """TODO."""

    def setUp(self) -> None:
        self.heading: str = 'test'
        self.scheduled: OrgDate = OrgDate(datetime(2023, 1, 1),
                                     datetime(2023, 1, 2))
        self.deadline: OrgDate = OrgDate(datetime(2023, 1, 1),
                                    datetime(2023, 1, 2))
        self.properties: dict = {'ID': '123',
                            'CALENDAR': 'outlook',
                            "LOCATION": 'Somewhere',
                            "ORGANIZER":  'Someone (someone@outlook.com)'}
        self.body: str = 'test'

        return super().setUp()
    def test_eq(self):
        """TODO.

        Args:
        ----
            self (): 
        """
        a = OrgAgendaItem(self.heading, self.scheduled, self.deadline, self.properties, self.body)
        b = OrgAgendaItem(self.heading, self.scheduled, self.deadline, self.properties, self.body)
        c = OrgAgendaItem('xxxxx', self.scheduled, self.deadline, self.properties, self.body)
        d = OrgAgendaItem(self.heading, None, self.deadline, self.properties, self.body)
        e = OrgAgendaItem(self.heading, self.scheduled, None, self.properties, self.body)
        f = OrgAgendaItem(self.heading, self.scheduled, self.deadline, {}, self.body)
        g = OrgAgendaItem(self.heading, self.scheduled, self.deadline, self.properties, '')

        self.assertTrue(a == b)
        self.assertFalse(a == c)
        self.assertFalse(a == d)
        self.assertFalse(a == e)
        self.assertFalse(a == f)
        self.assertFalse(a == g)

    def test_no_date(self):
        """TODO.

        Args:
        ----
            self (): 
        """
        with self.assertRaises(AssertionError):
            OrgAgendaItem('test')

    def test_one_date(self):
        """TODO.

        Args:
        ----
            self (): 
        """
        org_scheduled: OrgAgendaItem = OrgAgendaItem('test', scheduled=OrgDate(1))
        org_deadline: OrgAgendaItem = OrgAgendaItem('test', deadline=OrgDate(1))
        self.assertIsNone(org_scheduled.deadline)
        self.assertIsNone(org_deadline.scheduled)

    def test_form_org_node(self):
        pass
