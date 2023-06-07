from inspect import getfile
from os.path import dirname, expanduser, join

from khalorg import static

root: str = dirname(__file__)
config_dir: str = expanduser('~/.config/khalorg')
static_dir: str = dirname(getfile(static))

config: str = join(config_dir, 'config.ini')
format: str = join(config_dir, 'khalorg_format.txt')
khal_format: str = join(static_dir, 'khal_format.txt')
default_format: str = join(static_dir, 'khalorg_format.txt')
