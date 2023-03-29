from os.path import join
from test import static

from src.helpers import get_module_path


def get_test_config() -> str:
    path_static: str = get_module_path(static)
    return join(path_static, 'test_config_khal')


def read_org_test_file(org_file: str) -> str:
    """
    Reads an `org_file` and converts it into an `OrgNode` object. The
    directory is fixed and set to: /test/static/agenda_items.

    Args:
        org_file (str): path to an org file.

    Returns
    -------
        str: org file is converted to a string.

    """
    path: str = join(get_module_path(static), "agenda_items", org_file)
    with open(path) as org:
        return org.read()


def compare_without_white_space(a, b) -> bool:
    return compare_with_exclude(a, b, ('', '\n', '\t'))


def compare_with_exclude(a: str, b: str, excludes: tuple = tuple()) -> bool:
    return _filter(a, excludes) == _filter(b, excludes)


def _filter(text: str, excludes: tuple) -> list:
    return [x for x in text.splitlines() if x not in excludes]
