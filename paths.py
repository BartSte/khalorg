from os.path import dirname, join, expanduser

ROOT: str = dirname(__file__)
CONFIG_DIR: str = expanduser('~/.config/khalorg')
CONFIG: str = join(CONFIG_DIR, 'config.ini')
