import sys
from os.path import join
from test import static
from test.static.agenda_items import (
    MaximalValid,
    MinimalValid,
    MultipleTimstampsValid,
    NotFirstLevel,
    NoTimestamp,
    BodyFirst
)
from typing import Any
from unittest import TestCase
from unittest.mock import patch

from orgparse import loads
from orgparse.node import OrgNode

from src.helpers import get_module_path
from src.org_items import NvimOrgDate, OrgAgendaItem, OrgAgendaItemError


class TestNvimOrgDate(TestCase):
    def test(self):
        """Should print a date that is compatible with nvim-orgmode."""
        actual: str = str(
            NvimOrgDate(
                (2023, 1, 1, 1, 0, 0),
                (2023, 1, 1, 2, 0, 0)))
        expected: str = "<2023-01-01 Sun 01:00-02:00>"
        self.assertEqual(actual, expected)


class TestOrgAgendaItem(TestCase):
    """Test for OrgAgendaItem."""

    def test_eq(self):
        """Two objects with the same arguments must be equal."""
        a: OrgAgendaItem = OrgAgendaItem(*MaximalValid.get_args())
        b: OrgAgendaItem = OrgAgendaItem(*MaximalValid.get_args())
        self.assertTrue(a == b)

    def test_not_eq(self):
        """Two objects with different args should not be equal."""
        dummy_args = ["x", [NvimOrgDate(1)], NvimOrgDate(1), None, {}, ""]
        agenda_item: OrgAgendaItem = OrgAgendaItem(*MaximalValid.get_args())
        for count, x in enumerate(dummy_args):
            args: list = list(MaximalValid.get_args())  # copy object
            args[count] = x
            other_agenda_item = OrgAgendaItem(*args)
            self.assertTrue(agenda_item != other_agenda_item)

    def test_load_from_org_node_valid(self):
        """An agenda item generated from "Valid" or 'valid.org' must be the
        same.
        """
        org_file_vs_obj: tuple = (
            ("body_first.org", BodyFirst),
            ("maximal_valid.org", MaximalValid),
            ("minimal_valid.org", MinimalValid),
            ("multiple_timestamps.org", MultipleTimstampsValid),
            ("no_time_stamp.org", NoTimestamp),
            ("not_first_level.org", NotFirstLevel),
        )

        for file_, obj in org_file_vs_obj:
            agenda_item: OrgAgendaItem = OrgAgendaItem(*obj.get_args())
            is_equal, message = self._agenda_item_file_vs_object(file_,
                                                                 agenda_item)
            self.assertTrue(is_equal, message)

    def _agenda_item_file_vs_object(
            self,
            org_file: str,
            expected: OrgAgendaItem) -> tuple:
        """
        TODO.

        Args:
            org_file:
            expected_args:

        Returns
        -------

        """
        node: OrgNode = loads(self.read_org_test_file(org_file))
        actual: OrgAgendaItem = OrgAgendaItem().load_from_org_node(node)

        message: str = (
            f"\nFor org file: {org_file} an error is found:"
            f"\n\nActual is:\n{actual.__dict__}"
            f"\n\nExpected is:\n{expected.__dict__}"
        )
        return actual == expected, message

    def read_org_test_file(self, org_file: str) -> str:
        """
        Reads an `org_file` and converts it into an `OrgNode` object. The
        directory is fixed and set to: /test/static/agenda_items.

        Args:
            org_file (str): path to an org file.

        Returns
        -------
            str: org file is converted to a string.

        """
        path: str = join(get_module_path(static), "agenda_items", org_file)
        with open(path) as org:
            return org.read()

    def test_from_org_node_no_heading(self):
        """An agenda item generated from 'no_heading.org' must raise an error as
        the OrgNode does not have a child node.
        """
        with self.assertRaises(OrgAgendaItemError):
            node: OrgNode = loads(self.read_org_test_file("no_heading.org"))
            OrgAgendaItem().load_from_org_node(node)

    def test_not_first_child_or_heading(self):
        """
        No timestamps are found if the agenda item is not the first child of a
        node.
        """
        org_files: tuple = ('not_first_child.org', 'not_first_heading.org')
        for file_ in org_files:
            node: OrgNode = loads(self.read_org_test_file(file_))
            item: OrgAgendaItem = OrgAgendaItem().load_from_org_node(node)
            self.assertEqual(item.heading, "Heading")
            self.assertFalse(item.time_stamps)

    @patch.object(sys.stdin, "read")
    def test_load_from_stdin(self, patch_stdin: Any):
        """Reading an org file from stdn or from an OrgNode must give the same
        result.

        Args:
        ----
            patch_stdin: stdin's read function is patched
        """
        org_file: str = self.read_org_test_file("maximal_valid.org")
        patch_stdin.return_value = org_file
        node: OrgNode = loads(org_file)

        actual: OrgAgendaItem = OrgAgendaItem().load_from_stdin()
        expected: OrgAgendaItem = OrgAgendaItem().load_from_org_node(node)

        self.assertTrue(actual == expected)
