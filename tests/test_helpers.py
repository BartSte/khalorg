from datetime import date, datetime
from unittest import TestCase

import pytz
from khalorg.khal.helpers import set_tzinfo


class TestAddTzinfo(TestCase):

    def setUp(self) -> None:
        self.time: datetime = datetime(2023, 1, 1, 0, 0)
        self.date: date = datetime.date(self.time)
        self.timezone = pytz.timezone('Europe/Berlin')
        return super().setUp()

    def test_datetime(self):
        """
        When trying to add a timezone to a datetime, the timezone is
        changed.
        """
        expected = self.timezone.localize(self.time)
        actual = set_tzinfo(self.time, self.timezone)
        assert actual == expected

    def test_europe_berlin(self):
        """ When trying to add a timezone to a date, nothing changes. """
        assert set_tzinfo(self.date, self.timezone) == self.date
