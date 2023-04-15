from argparse import ArgumentParser

from src.commands import list_command, new


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
    child_new.add_argument('calendar', **Args.calendar)
    child_new.set_defaults(func=new)

    child_list: ArgumentParser = subparsers.add_parser(
        'list', **ParserInfo.list_command)
    child_list.add_argument('calendar', **Args.calendar)
    child_list.add_argument('start', **Args.start)
    child_list.add_argument('stop', **Args.stop)
    child_list.set_defaults(func=list_command)

    return parent


class ParserInfo:
    """ Constructor arguments for the ArgumentParser objects."""

    parent: dict = dict(
        prog='khalorg',
        description='Interface between Khal and Orgmode.')

    new: dict = dict(
        prog='khalorg new',
        description='Create a new khal item from an org item.')

    list_command: dict = dict(
        prog='khalorg list', description='Export khal items to org items')


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
