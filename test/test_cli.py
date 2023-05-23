import logging
import test
from os.path import join
from subprocess import CalledProcessError, check_output
from unittest import TestCase

from src.helpers import get_default_khalorg_format, get_module_path


def khalorg_tester(args: list) -> str:
    """Runs `/test/khalorg_tester` with `args` as command line arguments."""
    test_dir: str = get_module_path(test)
    cli_tester: list = [join(test_dir, 'khalorg_tester')]

    try:
        return check_output(cli_tester + args).decode()
    except CalledProcessError as error:
        logging.critical(error.output.decode())
        return ''


class TestNew(TestCase):

    def test(self):
        """
        When feeding a set of command line args, an expected set of
        function arguments for src.cli.new is expected.
        """
        args: list = ['--loglevel', 'CRITICAL', 'new', 'calendar']
        actual = khalorg_tester(args)
        expected: str = "'loglevel': 'CRITICAL', 'calendar': 'calendar'"
        self.assertTrue(expected in actual)


class TestEdit(TestCase):

    def test(self):
        """
        When feeding a set of command line args, an expected set of
        function arguments for src.cli.edit is expected.
        """
        args: list = [
            '--loglevel',
            'CRITICAL',
            'edit',
            'calendar',
            '--edit_dates'
        ]
        actual = khalorg_tester(args)
        expected: str = (
            "'loglevel': 'CRITICAL', "
            "'edit_dates': True, "
            "'calendar': 'calendar'"
        )
        self.assertTrue(expected in actual)

    def test_no_edit_dates(self):
        """
        When feeding a set of command line args, an expected set of
        function arguments for src.cli.edit is expected.
        """
        args: list = [
            '--loglevel',
            'CRITICAL',
            'edit',
            'calendar'
        ]
        actual = khalorg_tester(args)
        expected: str = (
            "'loglevel': 'CRITICAL', "
            "'edit_dates': False, "
            "'calendar': 'calendar'"
        )
        self.assertTrue(expected in actual)


class TestList(TestCase):

    def test(self):
        """
        When feeding a set of command line args, an expected set of
        function arguments for src.cli.list is expected.
        """
        default_format: str = get_default_khalorg_format()
        args: list = [
            '--loglevel',
            'CRITICAL',
            'list',
            '--format',
            default_format,
            'calendar',
            'today',
            '2d'
        ]
        actual = khalorg_tester(args)
        expected: str = (
            "'loglevel': 'CRITICAL', "
            f"'format': {repr(default_format)}, "
            "'calendar': 'calendar', "
            "'start': 'today', "
            "'stop': '2d'"
        )
        self.assertTrue(expected in actual, msg=actual)

    def test_minimal(self):
        """
        When feeding a set of command line args, an expected set of
        function arguments for src.cli.list is expected.
        """
        default_format: str = get_default_khalorg_format()
        args: list = [
            'list',
            'calendar',
        ]
        actual = khalorg_tester(args)
        expected: str = (
            "'loglevel': 'WARNING', "
            f"'format': {repr(default_format)}, "
            "'calendar': 'calendar', "
            "'start': 'today', "
            "'stop': '1d'"
        )
        self.assertTrue(expected in actual, msg=actual)
