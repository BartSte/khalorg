from argparse import ArgumentParser, RawDescriptionHelpFormatter

from src.commands import list_command, new, edit
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


_NEW_DESCRIPTION: str = """Create a new khal item from an org item.

An org agenda item can be converted to a new khal agenda item by feeding the
org item through stdin to `khalorg new` and specifying the khal calendar name
as a positional argument.

The following repeats are supported: daily, weekly, monthly or yearly. The
events repeat forever, unless you specify an end date using the `--until`
option."""

_LIST_DESCRIPTION: str = """List khal items as org items.

Agenda items from `khal` can be converted to org items using the `khalorg list`
command. For example:

khalorg list my_calendar today 90d > my_calendar.org

Here, the `khal` agenda items of the calendar `my_calendar` are converted to
org format and written to a file called `my_calendar.org`. The range is
specified from `today` till `90d` (90 days) in the future.

If ~khalorg list --format~ option is not defined, the default one is used
which can be found at `./src/static/khalorg_format.txt`. If you want to
define your own format, you have 2 options: you can use the
`khalorg list --format` option, or you can place your custom format at
`$HOME/.config/khalorg/khalorg_format.txt` this format will then be used
instead of the default.

The following keys are supported:
- attendees     - calendar
- categories    - description.
- location      - organizer
- rrule         - status
- timestamps    - title
- uid           - url
"""

_EDIT_DESCRIPTION = """Edit and existing khal event.
"""

class ParserInfo:
    """ Constructor arguments for the ArgumentParser objects."""

    parent: dict = dict(
        prog='khalorg',
        formatter_class=RawDescriptionHelpFormatter,
        description='Interface between Khal and Orgmode.')

    new: dict = dict(
        prog='khalorg new',
        formatter_class=RawDescriptionHelpFormatter,
        description=_NEW_DESCRIPTION)

    list_command: dict = dict(
        formatter_class=RawDescriptionHelpFormatter,
        prog='khalorg list', description=_LIST_DESCRIPTION)

    edit: dict = dict(
        prog='khalorg edit', description=_EDIT_DESCRIPTION)


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
