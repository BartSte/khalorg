from os.path import join
from test import static

from src.helpers import get_module_path


def get_test_config() -> str:
    path_static: str = get_module_path(static)
    return join(path_static, 'test_config_khal')

