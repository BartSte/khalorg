from datetime import datetime
from os.path import join
from test import static
from test.static.agenda_items import Valid
from unittest import TestCase

from orgparse import loads
from orgparse.node import OrgNode

from src.tools import OrgAgendaItem


class TestOrgAgendaItem(TestCase):
    """TODO."""

    def test_eq(self):
        """TODO.

        Args:
        ----
            self ():
        """
        a: OrgAgendaItem = OrgAgendaItem(*Valid.args)
        b: OrgAgendaItem = OrgAgendaItem(*Valid.args)
        self.assertTrue(a == b)

    def test_not_eq(self):
        """

        Args:
        ----
            self ():
        """
        a: OrgAgendaItem = OrgAgendaItem(*Valid.args)
        for count, x in enumerate(['x', datetime(2024, 1, 1), None, {}, '']):
            other_args: list = list(Valid.args)  # copy object
            other_args[count] = x
            b = OrgAgendaItem(*other_args)
            self.assertTrue(a != b)

    def test_different_args(self):
        """

        Args:
        ----
            self ():
        """
        a: OrgAgendaItem = OrgAgendaItem(*Valid.args)
        b: OrgAgendaItem = OrgAgendaItem(*Valid.args[:3])
        self.assertFalse(a == b)

    def test_form_org_node(self):
        #TODO the body contains a time stamp. We do not want that.
        org_file: str = join(static.__path__[0], 'agenda_items', 'valid.org')
        with open(org_file) as org:
            content: str = org.read()
            node: OrgNode = loads(content)

        actual: OrgAgendaItem = OrgAgendaItem.from_org_node(node)
        expected: OrgAgendaItem = OrgAgendaItem(*Valid.args)

        message: str = (f'\n\nActual is: {actual.__dict__}'
                        f'\n\nExpexted is: {expected.__dict__}')
        self.assertTrue(actual == expected, msg=message)
