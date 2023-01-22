from datetime import datetime
from dateutil import parser
import logging
import subprocess
from subprocess import CalledProcessError
from typing import Callable
from unittest import TestCase
from unittest.mock import patch

from click import command

from src.khal_interface import Command, Calendar


class TestCommand(TestCase):

    def setUp(self) -> None:
        logging.basicConfig(level=logging.DEBUG)
        return super().setUp()

    def test_command(self):
        khal: Callable = Command('khal', options=('--help',))
        try:
            khal(('--help',))
        except CalledProcessError as error:
            self.fail(error.stdout)

    def test_call(self):
        command: str = 'khal new'
        args: tuple = ('a', 'b', '-c', '--d')
        expected: list = [command, *args]
        new_item = Command(command)
        with patch.object(subprocess, 'check_output') as mock:
            new_item(args)
            mock.assert_called_with(expected)

class TestCalendar(TestCase):
    def test_longdateformat(self):
        calendar: Calendar = Calendar('outlook')
        print(calendar.long_datetime_format)

