from datetime import datetime
from os.path import join
from test import static
from unittest import TestCase

from orgparse import loads
from orgparse.date import OrgDate
from orgparse.node import OrgNode

from src.tools import OrgAgendaItem


class TestOrgAgendaItem(TestCase):
    """TODO."""

    def setUp(self) -> None:
        self.org_file: str = join(static.__path__[0], 'valid.org')

        self.heading: str = 'Meeting'
        self.time_stamp: OrgDate = OrgDate(datetime(2023, 1, 1, 11, 0))
        self.scheduled: OrgDate = OrgDate(datetime(2023, 1, 1, 12, 0),
                                          datetime(2023, 1, 1, 13, 0))
        self.deadline: OrgDate = OrgDate(datetime(2023, 1, 10, 14, 0))
        self.properties: dict = {'ID': '123',
                                 'CALENDAR': 'outlook',
                                 "LOCATION": 'Somewhere',
                                 "ORGANIZER": 'Someone (someone@outlook.com)'}
        self.body: str = "Hello,\n\nLets have a meeting\n\nRegards,\n\n\nSomeone"

        self.args: list = [self.heading, self.time_stamp, self.scheduled,
                           self.deadline, self.properties, self.body]

        return super().setUp()

    def test_eq(self):
        """TODO.

        Args:
        ----
            self ():
        """
        a: OrgAgendaItem = OrgAgendaItem(*self.args)
        b: OrgAgendaItem = OrgAgendaItem(*self.args)
        self.assertTrue(a == b)

    def test_not_eq(self):
        """

        Args:
        ----
            self ():
        """
        a: OrgAgendaItem = OrgAgendaItem(*self.args)
        for count, x in enumerate(['x', None, None, {}, '']):
            other_args: list = list(self.args)  # copy object
            other_args[count] = x
            b = OrgAgendaItem(*other_args)
            self.assertTrue(a != b)

    def test_different_args(self):
        """

        Args:
        ----
            self ():
        """
        a: OrgAgendaItem = OrgAgendaItem(*self.args)
        b: OrgAgendaItem = OrgAgendaItem(*self.args[:3])
        self.assertFalse(a == b)

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
        org_scheduled: OrgAgendaItem = OrgAgendaItem(
            'test', scheduled=OrgDate(1))
        org_deadline: OrgAgendaItem = OrgAgendaItem('test', deadline=OrgDate(1))
        self.assertFalse(bool(org_scheduled.deadline))
        self.assertFalse(bool(org_deadline.scheduled))

    def test_form_org_node(self):
        with open(self.org_file) as org:
            content: str = org.read()
            node: OrgNode = loads(content)
        a: OrgAgendaItem = OrgAgendaItem.from_org_node(node)
        b: OrgAgendaItem = OrgAgendaItem(*self.args)

        message: str = f'\n\na is: {a.__dict__}\n\nb is: {b.__dict__}'
        #TODO add assert
