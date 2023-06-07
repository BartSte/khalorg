
from unittest import TestCase

from orgparse.date import OrgDate

from khalorg.org.helpers import timestamp_to_orgdate


class TestTimestampToOrgdat(TestCase):

    DATE: str = '2023-01-02 Mon'
    EXPECTED: OrgDate = OrgDate.from_str(DATE)

    def test_inactive(self):
        """ Supports inactive org timestamp."""
        inactive: str = '[' + self.DATE + ']'
        assert self.EXPECTED == timestamp_to_orgdate(inactive)

    def test_plain(self):
        """ Supports plain org timestamp."""
        inactive: str = '<' + self.DATE + '>'
        assert self.EXPECTED == timestamp_to_orgdate(inactive)

    def test_normal(self):
        """ Supports normal date. """
        assert self.EXPECTED == timestamp_to_orgdate(self.DATE)
