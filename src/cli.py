from argparse import ArgumentParser, RawDescriptionHelpFormatter
from functools import partial
from os.path import join

import paths
from src.commands import edit, list_command, new
from src.helpers import get_khalorg_format


def get_parser() -> ArgumentParser:
    """
    Returns an ArgumentParser object for khalorg.

    Returns
    -------
        an ArgumentParser object.

    """
    parent: ArgumentParser = ArgumentParser(**ParserInfo.parent)
    parent.add_argument('--loglevel', **Args.loglevel)
    subparsers = parent.add_subparsers()

    child_new: ArgumentParser = subparsers.add_parser('new', **ParserInfo.new)
    child_new.add_argument('--until', **Args.until)
    child_new.add_argument('calendar', **Args.calendar)
    child_new.set_defaults(func=new)

    child_list: ArgumentParser = subparsers.add_parser('list', **ParserInfo.list_command)  # noqa
    child_list.add_argument('--format', **Args.format)
    child_list.add_argument('calendar', **Args.calendar)
    child_list.add_argument('start', **Args.start)
    child_list.add_argument('stop', **Args.stop)
    child_list.set_defaults(func=list_command)

    child_list: ArgumentParser = subparsers.add_parser('edit', **ParserInfo.edit)  # noqa
    child_list.add_argument('calendar', **Args.calendar)
    child_list.set_defaults(func=edit)

    return parent


def _read_static_txt(name: str) -> str:
    path: str = join(paths.static_dir, name)
    with open(path) as file_:
        return file_.read()


class ParserInfo:
    """ Constructor arguments for the ArgumentParser objects."""

    parent: dict = dict(
        prog='khalorg',
        formatter_class=RawDescriptionHelpFormatter,
        description='Interface between Khal and Orgmode.')

    new: dict = dict(
        prog='khalorg new',
        formatter_class=RawDescriptionHelpFormatter,
        description=_read_static_txt('description_new_command.txt')
    )

    list_command: dict = dict(
        formatter_class=RawDescriptionHelpFormatter,
        prog='khalorg list',
        description=_read_static_txt('description_list_command.txt')
    )

    edit: dict = dict(
        prog='khalorg edit',
        description=_read_static_txt('description_edit_command.txt')
    )


class Args:
    """ Arguments for the ArgumentParser.add_argument methods."""

    calendar: dict = dict(
        type=str,
        help=('Set the name of the khal calendar.')
    )

    loglevel: dict = dict(
        required=False,
        default='WARNING',
        help=('Set the logging level to: CRITICAL, ERROR, WARNING '
              '(default), INFO, DEBUG')
    )

    until: dict = dict(
        required=False,
        default='',
        type=str,
        help=('Stop an event repeating on this date.')
    )

    start: dict = dict(
        type=str,
        default='today',
        nargs='?',
        help=('Start date (default: today)'))

    stop: dict = dict(
        type=str,
        default='1d',
        nargs='?',
        help=('End date (default: 1d)'))

    format: dict = dict(
        type=str,
        default=get_khalorg_format(),
        help='The format of the events.'
    )
