from test.agenda_items import (
    AllDay,
    AllDayRecurring,
    BodyFirst,
    Minimal,
    MultipleTimstampsValid,
    NotFirstLevel,
    NoTimestamp,
    Recurring,
    ShortTimestamp,
    Valid,
)
from test.helpers import (
    read_org_test_file,
)
from unittest import TestCase

from orgparse import loads
from orgparse.date import OrgDate
from orgparse.node import OrgNode

import paths
from src.org.agenda_items import (
    EmptyOrgItemError,
    OrgAgendaFile,
    OrgAgendaItem,
    OrgDateAgenda,
)
from src.org.helpers import remove_timestamps


class TestOrgAgendaItem(TestCase):
    """Test for OrgAgendaItem."""

    def test_eq(self):
        """Two objects with the same arguments must be equal."""
        a: OrgAgendaItem = OrgAgendaItem(*Valid.get_args())
        b: OrgAgendaItem = OrgAgendaItem(*Valid.get_args())
        self.assertTrue(a == b)

    def test_not_eq(self):
        """Two objects with different args should not be equal."""
        dummy_args = ["x", [OrgDate(1)], {}, ""]
        agenda_item: OrgAgendaItem = OrgAgendaItem(*Valid.get_args())
        for count, x in enumerate(dummy_args):
            args: list = list(Valid.get_args())  # copy object
            args[count] = x
            other_agenda_item = OrgAgendaItem(*args)
            self.assertTrue(agenda_item != other_agenda_item)

    def test_remove_timestamps(self):
        """ `time_stamp` should be removed from `text`. """
        text: str = (
            "<2023-01-01 Sun 01:00>--<2023-01-01 Sun 02:00>\nSome text\n<2023-01-01 Sun 01:00>"
        )
        expected: str = "Some text\n"
        actual: str = remove_timestamps(text)
        self.assertEqual(actual, expected)

    def test_load_from_org_node_valid(self):
        """
        An agenda item generated from "Valid" or 'valid.org' must be the
        same.
        """
        org_file_vs_obj: tuple = (
            ("body_first.org", BodyFirst),
            ("valid.org", Valid),
            ("minimal.org", Minimal),
            ("multiple_timestamps.org", MultipleTimstampsValid),
            ("multiple_timestamps_unsorted.org", MultipleTimstampsValid),
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
        ----
            org_file: situated in ./test/static/agenda_item/
            expected: the expected OrgAgendaItem.

        Returns:
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
        with self.assertRaises(EmptyOrgItemError):
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

    def test_get_attendees(self):
        """
        The attendees in the OrgAgendaItem.properties should be parsed as a
        list.
        """
        item: OrgAgendaItem = OrgAgendaItem()
        item.properties['ATTENDEES'] = (
            'test@test.com, test2@test.com, test3@test.com'
        )
        actual: list = item.split_property('ATTENDEES')
        expected: list = ['test@test.com', 'test2@test.com', 'test3@test.com']
        self.assertEqual(actual, expected)

    def test_until_datetime(self):
        """
        When until is a datetime, and the start and end are datetime,
        do nothing.
        """
        item: OrgAgendaItem = OrgAgendaItem()
        text: str = read_org_test_file('valid.org')
        item.load_from_str(text)

        expected: OrgDate = OrgDate((2023, 1, 2, 0, 0))
        self.assertEqual(expected, item.until)

    def test_until_datetime_inactive(self):
        """Inactive timestamps are also supported."""
        item: OrgAgendaItem = OrgAgendaItem()
        text: str = read_org_test_file('valid_inactive_until.org')
        item.load_from_str(text)

        expected: OrgDate = OrgDate((2023, 1, 2, 0, 0))
        self.assertEqual(expected, item.until)

    def test_until_date(self):
        """
        When until is a date, and the start and end are datetime, converst
        until to a date time.
        """
        item: OrgAgendaItem = OrgAgendaItem()
        text: str = read_org_test_file('all_day.org')
        item.load_from_str(text)

        expected: OrgDate = OrgDate((2023, 1, 2))
        self.assertEqual(expected, item.until)

    def test_until_date_until_with_time(self):
        """
        When until is a datetime, and the start and end are date objects,
        convert unil to a date.
        """
        item: OrgAgendaItem = OrgAgendaItem()
        text: str = read_org_test_file('all_day_until_with_time.org')
        item.load_from_str(text)

        expected: OrgDate = OrgDate((2023, 1, 2))
        self.assertEqual(expected, item.until)


class TestAgendaOrgDates(TestCase):
    """ Test if duplicated items are removed. """

    def test_orgdates(self):
        orgs: tuple = (
            ("valid.org", Valid),
            ("rrule_recurring.org", Recurring),
            ("body_first.org", BodyFirst),
            ("not_first_level.org", NotFirstLevel),
            ("all_day.org", AllDay),
            ("rrule_recurring_allday.org", AllDayRecurring),
            ("short_timestamp.org", ShortTimestamp),
        )
        for org, expected in orgs:
            item: str = read_org_test_file(org)
            nodes: OrgNode = loads(item)
            actual: OrgDateAgenda = OrgDateAgenda(nodes)

            self.assertEqual(actual.dates, expected.org_dates, msg=org)
            self.assertEqual(str(actual.dates['123']),
                             str(expected.org_dates['123']), msg=org)


class TestOrgAgendaFile(TestCase):

    def test(self):
        """
        Test the OrgDateAgendaFile for the default format, (without the
        RRULE property).
        """
        with open(paths.default_format) as f:
            khalorg_format: str = f.read()

        orgs: tuple = (
            ('rrule_recurring.org', 'recurring.org'),
            ('rrule_recurring_monthly.org', 'recurring_monthly.org'),
            ('rrule_recurring_allday.org', 'recurring_allday.org'),
            ('rrule_recurring_duplicates.org', 'recurring.org'),
            ('rrule_recurring_not_supported.org', 'valid.org'),
            ('rrule_recurring_1th.org', 'recurring.org'),
            ('rrule_recurring_and_non_recurring.org', 'recurring_and_non_recurring.org')
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


class TestOrgDateAgenda(TestCase):

    def test_get_rrulestr_supported(self):
        """
        The RRULE of the rrule_recurring.org should be the same as the
        OrgDateAgenda.get_rrulestr method returns.
        """
        org_file: str = read_org_test_file('rrule_recurring.org')
        self._test_get_rrulestr(org_file)

    def _test_get_rrulestr(self, org_file: str):
        node: OrgNode = loads(org_file).children[0]
        dates: OrgDateAgenda = OrgDateAgenda(node)

        expected: str = node.properties['RRULE']
        actual: str = dates.get_rrulestr(node.properties['UID'])
        assert expected == actual

    def test_get_rrulestr_unsupported(self):
        """
        The RRULE of the rrule_recurring_not_supported.org should be the
        same as the OrgDateAgenda.get_rrulestr method returns.
        """
        org_file: str = read_org_test_file('rrule_recurring_not_supported.org')
        self._test_get_rrulestr(org_file)
