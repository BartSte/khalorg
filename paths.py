from os.path import dirname, expanduser, join
from src import static

from src.helpers import get_module_path

root: str = dirname(__file__)
config_dir: str = expanduser('~/.config/khalorg')
static_dir: str = get_module_path(static)

config: str = join(config_dir, 'config.ini')
org_format: str = join(config_dir, 'org_format.txt')
