import logging
from os.path import join
from subprocess import CalledProcessError, check_output
from unittest import TestCase

from khalorg import paths
import tests
from khalorg.helpers import get_default_khalorg_format, get_khalorg_format
from tests.helpers import get_module_path


def khalorg_tester(args: list) -> str:
    """Runs `/test/khalorg_tester` with `args` as command line arguments."""
    test_dir: str = get_module_path(tests)
    cli_tester: list = ["python", join(test_dir, "khalorg_tester")]

    try:
        return check_output(cli_tester + args).decode()
    except CalledProcessError as error:
        logging.critical(error.output.decode())
        return ""


class TestNew(TestCase):
    def test(self):
        """
        When feeding a set of command line args, an expected set of
        function arguments for khalorg.cli.new is expected.
        """
        args: list = [
            "--loglevel",
            "CRITICAL",
            "--logfile",
            "foo",
            "new",
            "calendar",
        ]
        actual = khalorg_tester(args)
        expected: str = (
            "'loglevel': 'CRITICAL', 'logfile': 'foo', 'calendar': 'calendar'"
        )
        self.assertTrue(expected in actual)


class TestEdit(TestCase):
    def test(self):
        """
        When feeding a set of command line args, an expected set of
        function arguments for khalorg.cli.edit is expected.
        """
        args: list = [
            "--loglevel",
            "CRITICAL",
            "--logfile",
            "foo",
            "edit",
            "calendar",
            "--edit-dates",
        ]
        actual = khalorg_tester(args)
        expected: str = (
            "'loglevel': 'CRITICAL', "
            "'logfile': 'foo', "
            "'edit_dates': True, "
            "'calendar': 'calendar'"
        )
        self.assertTrue(expected in actual)

    def test_no_edit_dates(self):
        """
        When feeding a set of command line args, an expected set of
        function arguments for khalorg.cli.edit is expected.
        """
        args: list = [
            "--loglevel",
            "CRITICAL",
            "--logfile",
            "foo",
            "edit",
            "calendar",
        ]
        actual = khalorg_tester(args)
        expected: str = (
            "'loglevel': 'CRITICAL', "
            "'logfile': 'foo', "
            "'edit_dates': False, "
            "'calendar': 'calendar'"
        )
        self.assertTrue(expected in actual)


class TestList(TestCase):
    def test(self):
        """
        When feeding a set of command line args, an expected set of
        function arguments for khalorg.cli.list is expected.
        """
        default_format: str = get_default_khalorg_format()
        args: list = [
            "--loglevel",
            "CRITICAL",
            "--logfile",
            "foo",
            "list",
            "--format",
            default_format,
            "calendar",
            "today",
            "2d",
        ]
        actual = khalorg_tester(args)
        expected: str = (
            "'loglevel': 'CRITICAL', "
            "'logfile': 'foo', "
            f"'format': {repr(default_format)}, "
            "'calendar': 'calendar', "
            "'start': 'today', "
            "'stop': '2d'"
        )
        self.assertTrue(expected in actual, msg=actual)

    def test_minimal(self):
        """
        When feeding a set of command line args, an expected set of
        function arguments for khalorg.cli.list is expected.
        """
        default_format: str = get_khalorg_format()
        args: list = [
            "list",
            "calendar",
        ]
        actual = khalorg_tester(args)
        expected: str = (
            "'loglevel': 'WARNING', "
            f"'logfile': '{paths.log_file}', "
            f"'format': {repr(default_format)}, "
            "'calendar': 'calendar', "
            "'start': 'today', "
            "'stop': '1d'"
        )
        self.assertTrue(expected in actual, msg=actual)


class TestDelete(TestCase):
    def test(self):
        """
        When feeding a set of command line args, an expected set of
        function arguments for khalorg.cli.delete is expected.
        """
        args: list = [
            "--loglevel",
            "CRITICAL",
            "--logfile",
            "foo",
            "delete",
            "calendar",
        ]
        actual = khalorg_tester(args)
        expected: str = (
            "'loglevel': 'CRITICAL', "
            "'logfile': 'foo', "
            "'calendar': 'calendar'"
        )
        self.assertTrue(expected in actual)
