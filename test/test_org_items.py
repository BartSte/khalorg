import sys

from orgparse.date import OrgDate
from test.agenda_items import (
    AllDay,
    AllDayRecurring,
    BodyFirst,
    MaximalValid,
    MinimalValid,
    MultipleTimstampsValid,
    NotFirstLevel,
    NoTimestamp,
    Recurring,
    ShortTimestamp,
)
from test.helpers import (
    read_org_test_file,
)
from typing import Any
from unittest import TestCase
from unittest.mock import patch

from orgparse import loads
from orgparse.node import OrgNode

import paths
from src.org_items import (
    OrgAgendaFile,
    OrgAgendaItem,
    OrgAgendaItemError,
    OrgDateAgenda,
)


class TestOrgAgendaItem(TestCase):
    """Test for OrgAgendaItem."""

    def test_eq(self):
        """Two objects with the same arguments must be equal."""
        a: OrgAgendaItem = OrgAgendaItem(*MaximalValid.get_args())
        b: OrgAgendaItem = OrgAgendaItem(*MaximalValid.get_args())
        self.assertTrue(a == b)

    def test_not_eq(self):
        """Two objects with different args should not be equal."""
        dummy_args = ["x", [OrgDate(1)], NvimOrgDate(1), None, {}, ""]
        agenda_item: OrgAgendaItem = OrgAgendaItem(*MaximalValid.get_args())
        for count, x in enumerate(dummy_args):
            args: list = list(MaximalValid.get_args())  # copy object
            args[count] = x
            other_agenda_item = OrgAgendaItem(*args)
            self.assertTrue(agenda_item != other_agenda_item)

    def test_remove_timestamps(self):
        """ `time_stamp` should be removed from `text`. """
        text: str = (
            "<2023-01-01 Sun 01:00>--<2023-01-01 Sun 02:00>\nSome text\n<2023-01-01 Sun 01:00>"
        )
        time_stamp: list[OrgDate] = [
            OrgDate((2023, 1, 1, 1, 0, 0), (2023, 1, 1, 2, 0, 0)),
            OrgDate((2023, 1, 1, 1, 0, 0))
        ]
        expected: str = "Some text\n"
        actual: str = OrgAgendaItem.remove_timestamps(text, time_stamp)
        self.assertEqual(actual, expected)

    def test_load_from_org_node_valid(self):
        """
        An agenda item generated from "Valid" or 'valid.org' must be the
        same.
        """
        org_file_vs_obj: tuple = (
            ("body_first.org", BodyFirst),
            ("maximal_valid.org", MaximalValid),
            ("minimal_valid.org", MinimalValid),
            ("multiple_timestamps.org", MultipleTimstampsValid),
            ("no_time_stamp.org", NoTimestamp),
            ("not_first_level.org", NotFirstLevel),
            ("recurring.org", Recurring),
            ("all_day.org", AllDay),
            ("short_timestamp.org", ShortTimestamp),
        )

        for file_, obj in org_file_vs_obj:
            agenda_item: OrgAgendaItem = OrgAgendaItem(*obj.get_args())
            is_equal, message = self._agenda_item_file_vs_object(file_,
                                                                 agenda_item)
            self.assertTrue(is_equal, message)

    def _agenda_item_file_vs_object(
            self,
            org_file: str,
            expected: OrgAgendaItem) -> tuple[bool, str]:
        """
        Comapre an *.org file with a OrgAgendaItem.

        Args:
            org_file: situated in ./test/static/agenda_item/
            expected: the expected OrgAgendaItem.

        Returns
        -------
           bool represents the comparison, and an optional error message is
           provided as str.

        """
        node: OrgNode = loads(read_org_test_file(org_file))
        actual: OrgAgendaItem = OrgAgendaItem().load_from_org_node(node)

        message: str = (
            f"\nFor org file: {org_file} an error is found:"
            f"\n\nActual is:\n{actual.__dict__}"
            f"\n\nExpected is:\n{expected.__dict__}"
        )
        return actual == expected, message

    def test_from_org_node_no_heading(self):
        """
        An agenda item generated from 'no_heading.org' must raise an error as
        the OrgNode does not have a child node.
        """
        with self.assertRaises(OrgAgendaItemError):
            node: OrgNode = loads(read_org_test_file("no_heading.org"))
            OrgAgendaItem().load_from_org_node(node)

    def test_not_first_child_or_heading(self):
        """
        No timestamps are found if the agenda item is not the first child of a
        node.
        """
        org_files: tuple = ('not_first_child.org', 'not_first_heading.org')
        for file_ in org_files:
            node: OrgNode = loads(read_org_test_file(file_))
            item: OrgAgendaItem = OrgAgendaItem().load_from_org_node(node)
            self.assertEqual(item.title, "Heading")
            self.assertFalse(item.timestamps)

    @patch.object(sys.stdin, "read")
    def test_load_from_stdin(self, patch_stdin: Any):
        """
        Reading an org file from stdn or from an OrgNode must give the same
        result.

        Args:
        ----
            patch_stdin: stdin's read function is patched
        """
        org_file: str = read_org_test_file("maximal_valid.org")
        patch_stdin.return_value = org_file
        node: OrgNode = loads(org_file)

        actual: OrgAgendaItem = OrgAgendaItem().load_from_stdin()
        expected: OrgAgendaItem = OrgAgendaItem().load_from_org_node(node)

        self.assertTrue(actual == expected)

    def test_get_attendees(self):
        """
        The attendees in the OrgAgendaItem.properties should be parsed as a
        list.
        """
        item: OrgAgendaItem = OrgAgendaItem()
        item.properties['ATTENDEES'] = (
            'test@test.com, test2@test.com, test3@test.com'
        )
        actual: list = item.get_attendees()
        expected: list = ['test@test.com', 'test2@test.com', 'test3@test.com']
        self.assertEqual(actual, expected)


class TestAgendaOrgDates(TestCase):
    """ Test if duplicated items are removed. """

    def test_orgdates(self):
        orgs: tuple = (
            ("maximal_valid.org", MaximalValid),
            ("recurring.org", Recurring),
            ("body_first.org", BodyFirst),
            ("minimal_valid.org", MinimalValid),
            ("not_first_level.org", NotFirstLevel),
            ("all_day.org", AllDay),
            ("recurring.org", Recurring),
            ("recurring_allday.org", AllDayRecurring),
            ("short_timestamp.org", ShortTimestamp),
        )
        for org, expected in orgs:
            item: str = read_org_test_file(org)
            nodes: OrgNode = loads(item)
            actual: OrgDateAgenda = OrgDateAgenda(nodes)

            self.assertEqual(actual.dates, expected.org_dates, msg=org)
            self.assertEqual(str(actual.dates['123']),
                             str(expected.org_dates['123']), msg=org)


class TestCompose(TestCase):

    def test(self):
        with open(paths.default_format) as f:
            khalorg_format: str = f.read()

        orgs: tuple = (
            ('khal_list_recurring.org', 'recurring.org'),
            ('khal_list_recurring_monthly.org', 'recurring_monthly.org'),
            ('khal_list_recurring_allday.org', 'recurring_allday.org'),
            ('khal_list_recurring_duplicates.org', 'recurring.org'),
            ('khal_list_recurring_not_supported.org', 'maximal_valid.org'),
            ('khal_list_recurring_1th.org', 'recurring.org'),
            ('khal_list_recurring_and_non_recurring.org', 'recurring_and_non_recurring.org')
        )

        for org, expected_org in orgs:
            item: str = read_org_test_file(org)
            agenda: OrgAgendaFile = OrgAgendaFile.from_str(item)
            agenda.apply_rrules()
            actual: str = format(agenda, khalorg_format)
            expected: str = read_org_test_file(expected_org)
            message: str = (
                f"\n\nFor org file: {org} an error is found:"
                f"\n\nActual is:\n{actual}"
                f"\n\nExpected is:\n{expected}"
            )
            self.assertEqual(actual, expected, msg=message)
