from configparser import ConfigParser
from os.path import join

from munch import Munch
from src.org_items import remove_duplicates
from test import static
from unittest import TestCase

from src.helpers import get_config, get_module_path
from test.helpers import read_org_test_file


class TestGetConfig(TestCase):
    """Test the Config class.

    Attributes
    ----------
        user: path to a user config.
        default: path to a default config.
        combined: combined config of user and default
    """

    def setUp(self) -> None:
        dir_static: str = get_module_path(static)
        self.user: str = join(dir_static, 'test_config_user.ini')
        self.default: str = join(dir_static, 'test_config_default.ini')
        self.combined: str = join(dir_static, 'test_config_combined.ini')
        return super().setUp()

    def test_read(self):
        """
        When combining `user` and `default` the resulting dict should be
        the same as TestConfigFile.combined.
        """
        configs: list = [self.default, self.user, 'non_existing.ini']
        actual: Munch = get_config(configs)
        expected: ConfigParser = ConfigParser()

        expected.read(self.combined)

        self.assertEqual(dict(actual), dict(expected))

class TestRemoveDuplicates(TestCase):

    def test(self):
        items: str = read_org_test_file("duplicate.org")
        remove_duplicates(items)
        # TODO: continue here. This function works but it should not remove
        # repeated items, only those that are caused by non-repeatable items
        # (multi-day items)
        
