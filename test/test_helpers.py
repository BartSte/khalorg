from configparser import ConfigParser
from os.path import join
from tempfile import NamedTemporaryFile
from test import static
from unittest import TestCase

from src.helpers import Config, get_module_path


class TestConfigFile(TestCase):
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

    def test_combine(self):
        """
        When combining `user` and `default` the resulting dict should be
        the same as TestConfigFile.combined.
        """
        config: Config = Config()
        actual: ConfigParser = ConfigParser()
        expected: ConfigParser = ConfigParser()

        with NamedTemporaryFile() as f:
            config.combine(f.name, [self.default, self.user])
            actual.read(f.name)

        expected.read(self.combined)
        self.assertEqual(dict(actual), dict(expected))
