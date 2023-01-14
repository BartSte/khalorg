from datetime import datetime
from os.path import join
from test import static
from test.static.agenda_items import (
    MaximalValid,
    MinimalValid,
    MultipleTimstampsValid,
)
from unittest import TestCase

from orgparse import loads
from orgparse.node import OrgNode

from src.org_items import OrgAgendaItem
from src.tools import get_module_path


class TestOrgAgendaItem(TestCase):
    """Test for OrgAgendaItem."""

    def test_eq(self):
        """Two objects with the same arguments must be equal."""
        a: OrgAgendaItem = OrgAgendaItem(*MaximalValid.args)
        b: OrgAgendaItem = OrgAgendaItem(*MaximalValid.args)
        self.assertTrue(a == b)

    def test_not_eq(self):
        """Two objects with different args should not be equal."""
        dummy_args = ['x', datetime(2024, 1, 1), None, {}, '']
        agenda_item: OrgAgendaItem = OrgAgendaItem(*MaximalValid.args)
        for count, x in enumerate(dummy_args):
            args: list = list(MaximalValid.args)  # copy object
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
        agenda_item: OrgAgendaItem = OrgAgendaItem(*MaximalValid.args[:2])
        self.assertEqual(MaximalValid.args[0], agenda_item.heading)
        self.assertEqual(MaximalValid.args[1], agenda_item.time_stamps)

    def test_from_org_node_valid(self):
        """An agenda item generated from "Valid" or 'valid.org' must be the
        same.
        """
        org_file_vs_args: tuple = (
            ('maximal_valid.org', MaximalValid.args),
            ('minimal_valid.org', MinimalValid.args),
            ('multiple_timestamps.org', MultipleTimstampsValid.args),
        )

        for org_file, args in org_file_vs_args:
            is_equal, message = self._org_is_equal(org_file, args)
            self.assertTrue(is_equal, message)

    def _org_is_equal(self, org_file: str, expected_args: list) -> tuple:
        """
        TODO.

        Args:
            org_file:
            expected_args:

        Returns
        -------

        """
        node: OrgNode = self.read_org(org_file)
        actual: OrgAgendaItem = OrgAgendaItem.from_org_node(node)
        expected: OrgAgendaItem = OrgAgendaItem(*expected_args)

        message: str = (
            f'\nFor org file: {org_file} an error is found:'
            f'\n\nActual is:\n{actual.__dict__}'
            f'\n\nExpexted is:\n{expected.__dict__}')
        return actual == expected, message

    def read_org(self, org_file: str) -> OrgNode:
        """
        Reads an `org_file` and converts it into an `OrgNode` object.

        The directory is fixed and set to: /test/static/agenda_items.

        Args:
            org_file (str): path to an org file.

        Returns
        -------
            OrgNode: org file is converted to a string.

        """
        path: str = join(get_module_path(static), 'agenda_items', org_file)
        with open(path) as org:
            return loads(org.read())

    # def test_from_org_node_invalid(self):
    #     """An agenda item generated from "Valid" or 'valid.org' must be the
    #     same.
    #     """
    #     org_file_vs_args: tuple = (
    #         ('', MaximalValid.args),
    #     )

    #     for org_file, args in org_file_vs_args:
    #         is_equal, message = self._org_is_equal(org_file, args)
    #         self.assertTrue(is_equal, message)
