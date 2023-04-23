from unittest import TestCase

from dateutil.rrule import rrule

from src.rrule import rrule_is_supported, rrulestr_to_org, rrulestr_to_rrule


class TestRepeater(TestCase):

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
        repeater: tuple = rrulestr_to_org(rule)
        self.assertEqual(repeater, ('+', '1', 'w'))

    def test_rrule_to_org_not_supported(self):
        rule: str = (
            'FREQ=WEEKLY;UNTIL=20230904T113000Z;INTERVAL=1;BYDAY=MO,TH;WKST=MO'
        )
        repeater: tuple = rrulestr_to_org(rule)
        self.assertEqual(repeater, ('', '', ''))
