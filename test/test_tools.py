from datetime import datetime
from os.path import join
from test import static
from test.static.agenda_items import Valid
from unittest import TestCase

from orgparse import loads
from orgparse.node import OrgNode

from src.tools import OrgAgendaItem, get_module_path


class TestOrgAgendaItem(TestCase):
    """Test for OrgAgendaItem."""

    def test_eq(self):
        """Two objects with the same arguments must be equal."""
        a: OrgAgendaItem = OrgAgendaItem(*Valid.args)
        b: OrgAgendaItem = OrgAgendaItem(*Valid.args)
        self.assertTrue(a == b)

    def test_not_eq(self):
        """Two objects with different args should not be equal."""
        dummy_args = ['x', datetime(2024, 1, 1), None, {}, '']
        agenda_item: OrgAgendaItem = OrgAgendaItem(*Valid.args)
        for count, x in enumerate(dummy_args):
            args: list = list(Valid.args)  # copy object
            args[count] = x
            other_agenda_item = OrgAgendaItem(*args)
            self.assertTrue(agenda_item != other_agenda_item)

    def test_different_args(self):
        """Supplying the heading and timestamp is the minimal we need for an
        agenda item.

        Args:
        ----
            self ():
        """
        agenda_item: OrgAgendaItem = OrgAgendaItem(*Valid.args[:2])
        self.assertEqual(Valid.args[0], agenda_item.heading)
        self.assertEqual(Valid.args[1], agenda_item.time_stamps)

    def test_from_org_node(self):
        """An agenda item generated from "Valid" or 'valid.org' must be the
        same.
        """
        node: OrgNode = self.read_org('valid.org')

        actual: OrgAgendaItem = OrgAgendaItem.from_org_node(node)
        expected: OrgAgendaItem = OrgAgendaItem(*Valid.args)

        message: str = (f'\n\nActual is: {actual.__dict__}'
                        f'\n\nExpexted is: {expected.__dict__}')
        self.assertTrue(actual == expected, msg=message)

    def read_org(self, org_file: str) -> OrgNode:
        """Reads an `org_file` and converts it into an `OrgNode` object. The
        directory is fixed and set to: /test/static/agenda_items.

        Args:
            org_file (str): path to an org file.

        Returns
        -------
            OrgNode: org file is converted to a string.

        """
        path: str = join(get_module_path(static), 'agenda_items', org_file)
        with open(path) as org:
            return loads(org.read())
