import logging
import test
from os.path import join
from subprocess import CalledProcessError, check_output
from unittest import TestCase

from src.helpers import get_module_path


class TestCLI(TestCase):

    def setUp(self) -> None:
        self.cli_tester: str = join(get_module_path(test),
                                    'org2khal_CLI_tester')
        return super().setUp()

    def test_with_args(self):
        """ Expected that the org2khal_CLI_tester executable return the
        calendar and the log level.
        """
        args: list = [self.cli_tester, 'calendar', '--logging', 'CRITICAL']
        try:
            stdout: bytes = check_output(args)
        except CalledProcessError as error:
            logging.critical(error.output)
            self.fail(error.output)
        else:
            self.assertEqual(stdout, b'calendar\nCRITICAL\n')
