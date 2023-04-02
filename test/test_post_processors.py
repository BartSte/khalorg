from os.path import join
from khal.cli import build_collection
from khal.settings.settings import find_configuration_file, get_config
from munch import Munch
from src.helpers import get_module_path
from test import static
from test.helpers import (
    compare_without_white_space,
    read_org_test_file,
)
from unittest import TestCase

from src.post_processors import Attendees, Export


class TestExport(TestCase):
    """ Test if duplicated items are removed. """

    def test_duplicates(self):
        """ A duplicate is present maximal_valid.org is duplicated. """
        post_processor: Export
        duplicate: str = read_org_test_file("duplicate.org")
        post_processor = Export.from_str(duplicate)

        expected: str = read_org_test_file("maximal_valid.org")
        actual: str = post_processor.remove_duplicates()

        self.assertTrue(compare_without_white_space(expected, actual))

    def test_no_duplicates(self):
        """ No duplicate is present so no changed are expected. """
        post_processor: Export
        expected: str = read_org_test_file("no_duplicates.org")

        post_processor = Export.from_str(expected)
        actual: str = post_processor.remove_duplicates()

        self.assertTrue(compare_without_white_space(expected, actual))


class TestAttendees(TestCase):
    # TODO: write test for this

    def test_init(self):
        pass

    def test_load(self):
        pass
        
    def test_update(self):
        pass
