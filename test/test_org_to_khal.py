import logging
import test
from os.path import join
from subprocess import PIPE, CalledProcessError, Popen, check_output
from unittest import TestCase

from src.helpers import get_module_path


class TestCLI(TestCase):

    def setUp(self) -> None:
        logging.basicConfig(level=logging.DEBUG)
        return super().setUp()

    def test_with_args(self):
        """ Expected that the org2khal_CLI_tester executable return the
        calendar and the log level.
        """
        cli_tester: str = join(get_module_path(test), 'org2khal_CLI_tester')
        args: list = [cli_tester, 'calendar', '--logging', 'CRITICAL']
        try:
            stdout: bytes = check_output(args)
        except CalledProcessError as error:
            logging.critical(error.output)
            self.fail(error.output)
        else:
            self.assertEqual(stdout, b'calendar\nCRITICAL\n')

    def test_new(self):
        """ Expected that the org2khal_CLI_tester executable return the
        calendar and the log level.
        """
        #TODO add assertion
        cli_tester: str = join(get_module_path(test), 'org2khal_tester')
        org_file: str = join(get_module_path(test), 'static', 'agenda_items',
                             'maximal_valid.org')
        cat_args: tuple = ('cat', org_file)
        args: tuple = (cli_tester, '--logging', 'CRITICAL', 'calendar')
        try:
            with Popen(cat_args, stdout=PIPE) as cat:
                stdout: bytes = check_output(args, stdin=cat.stdout)
                cat.wait()
        except CalledProcessError as error:
            logging.critical(error.output)
            self.fail(error.output)
        else:
            logging.info(stdout.decode())
