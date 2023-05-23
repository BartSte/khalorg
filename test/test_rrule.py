from datetime import datetime
from unittest import TestCase

from dateutil.rrule import rrule
from orgparse.date import OrgDate

from src.rrule import (
    get_rrulestr,
    rrule_is_supported,
    rrulestr_to_org,
    rrulestr_to_rrule,
)


class TestRrulestrToOrg(TestCase):

    def test_is_supported_true(self):
        rule: str = (
            'FREQ=WEEKLY;UNTIL=20230904T113000Z;INTERVAL=1;BYDAY=MO;WKST=MO'
        )
        obj: rrule = rrulestr_to_rrule(rule)
        self.assertTrue(rrule_is_supported(obj))

    def test_is_not_supported(self):
        rules: tuple = (
            'FREQ=WEEKLY;UNTIL=20230904T113000Z;INTERVAL=1;BYDAY=MO,TH;WKST=MO',
            'FREQ=WEEKLY;UNTIL=20230904T113000Z;INTERVAL=1;BYWEEKNO=1;WKST=MO')
        for rule in rules:
            obj: rrule = rrulestr_to_rrule(rule)
            self.assertFalse(rrule_is_supported(obj))

    def test_rrule_to_org(self):
        rule: str = (
            'FREQ=WEEKLY;UNTIL=20230904T113000Z;INTERVAL=1;BYDAY=MO;WKST=MO'
        )
        repeater: tuple | None = rrulestr_to_org(rule)
        self.assertEqual(repeater, ('+', 1, 'w'))

    def test_rrule_to_org_not_supported(self):
        rule: str = (
            'FREQ=WEEKLY;UNTIL=20230904T113000Z;INTERVAL=1;BYDAY=MO,TH;WKST=MO'
        )
        repeater: tuple | None = rrulestr_to_org(rule)
        self.assertIsNone(repeater)


class TestGetRrule(TestCase):

    def test_not_recurring(self):
        date: OrgDate = OrgDate(start=datetime.now())
        result: str = get_rrulestr(date)
        self.assertFalse(result)

    def test_not_supported(self):
        date: OrgDate = OrgDate(start=datetime.now(), repeater=('+', 'x', 'x'))
        result: str = get_rrulestr(date)
        self.assertFalse(result)

    def test_weekly(self):
        date: OrgDate = OrgDate(start=datetime.now(), repeater=('+', 2, 'w'))
        result: str = get_rrulestr(date, clip=True)
        self.assertEqual('FREQ=WEEKLY;INTERVAL=2', str(result))

    def test_monthly(self):
        date: OrgDate = OrgDate(start=datetime.now(), repeater=('+', 3, 'm'))
        result: str = get_rrulestr(date, clip=True)
        self.assertEqual('FREQ=MONTHLY;INTERVAL=3', str(result))
