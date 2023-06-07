from os.path import exists

from khalorg import paths


def get_khalorg_format():
    """
    Returns the user specified `khalorg list --format` optional argument.
    This format should be stored at the `~/.config/khalorg/khalorg_format.txt`
    file. This file does not exists untill it is created by the user.

    Returns
    -------
        the user-specific format.

    """
    path: str = paths.format if exists(paths.format) else paths.default_format
    with open(path) as file_:
        return file_.read()


def get_default_khalorg_format() -> str:
    """
    Returns the default format for the `khalorg list --format` option.

    Returns
    -------
       the format as a str
    """
    with open(paths.default_format) as file_:
        return file_.read()
