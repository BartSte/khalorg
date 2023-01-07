from os.path import join
from test import static
from unittest import TestCase


class TestParseOrgAgendaItem(TestCase):

    def setUp(self) -> None:
        dir_static: str = static.__path__[0]  # type:ignore
        self.valid_file: str = join(dir_static, 'valid.org')
        return super().setUp()

    def test_valid_item(self):
        pass
