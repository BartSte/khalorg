from test.helpers import (
    compare_without_white_space,
    read_org_test_file,
)
from unittest import TestCase

from src.post_processors import List


class TestList(TestCase):
    """ Test if duplicated items are removed. """

    def test_duplicates(self):
        """ A duplicate is present maximal_valid.org is duplicated. """
        post_processor: List
        duplicate: str = read_org_test_file("duplicate.org")
        post_processor = List.from_str(duplicate)

        expected: str = read_org_test_file("maximal_valid.org")
        actual: str = post_processor.remove_duplicates()

        self.assertTrue(compare_without_white_space(expected, actual))

    def test_no_duplicates(self):
        """ No duplicate is present so no changed are expected. """
        post_processor: List
        expected: str = read_org_test_file("no_duplicates.org")

        post_processor = List.from_str(expected)
        actual: str = post_processor.remove_duplicates()

        self.assertTrue(compare_without_white_space(expected, actual))

