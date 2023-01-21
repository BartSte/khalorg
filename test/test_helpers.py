import logging
import test
from os.path import join
from subprocess import CalledProcessError, check_output
from unittest import TestCase

from src.helpers import get_module_path


class TestOrgToKhalParser(TestCase):
    """Test OrgToKhalParser."""

    def test_positional(self):
        """
        test_org_to_khal_parser binary is expected to return its positional
        and optional arguments.
        """
        program: str = join(get_module_path(test), 'test_org_to_khal_parser')
        positional: str = 'calendar'
        optional: str = 'CRITICAL'

        args: list = [program, positional, '--logging', optional]
        expected: str = ''.join(x + '\n' for x in (positional, optional))

        try:
            stdout: bytes = check_output(args)
        except CalledProcessError as error:
            logging.critical(error.output)
            self.fail(error.output)
        else:
            logging.debug(stdout)
            actual: str = stdout.decode()
            self.assertEqual(actual, expected)
