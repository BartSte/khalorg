from argparse import ArgumentParser, RawDescriptionHelpFormatter
from os.path import join

from khalorg import paths
from khalorg.commands import delete, edit, list_command, new, sync
from khalorg.helpers import get_khalorg_format


def get_parser() -> ArgumentParser:
    """
    Returns an ArgumentParser object for khalorg.

    Returns
    -------
        an ArgumentParser object.

    """
    parent: ArgumentParser = ArgumentParser(**ParserInfo.parent)
    parent.add_argument("--loglevel", **Args.loglevel)
    parent.add_argument("--logfile", **Args.logfile)
    subparsers = parent.add_subparsers(required=True)

    child_new: ArgumentParser = subparsers.add_parser("new", **ParserInfo.new)
    child_new.add_argument("calendar", **Args.calendar)
    child_new.set_defaults(func=new)

    child_list: ArgumentParser = subparsers.add_parser(
        "list", **ParserInfo.list_command
    )  # noqa
    child_list.add_argument("--format", **Args.format)
    child_list.add_argument("calendar", **Args.calendar)
    child_list.add_argument("start", **Args.start)
    child_list.add_argument("stop", **Args.stop)
    child_list.set_defaults(func=list_command)

    child_edit: ArgumentParser = subparsers.add_parser(
        "edit", **ParserInfo.edit
    )  # noqa
    child_edit.add_argument("--edit-dates", **Args.edit_dates)
    child_edit.add_argument("calendar", **Args.calendar)
    child_edit.set_defaults(func=edit)

    child_delete: ArgumentParser = subparsers.add_parser(
        "delete", **ParserInfo.delete
    )  # noqa
    child_delete.add_argument("calendar", **Args.calendar)
    child_delete.set_defaults(func=delete)

    child_sync: ArgumentParser = subparsers.add_parser(
        "sync", **ParserInfo.sync
    )  # noqa
    child_sync.add_argument("--format", **Args.format)
    child_sync.add_argument("--start", **Args.start)
    child_sync.add_argument("--stop", **Args.stop_sync)
    child_sync.add_argument("--edit-dates", **Args.edit_dates)
    child_sync.add_argument("--state-dir", **Args.state_dir)
    child_sync.add_argument("--conflict-resolution", **Args.conflict_resolution)
    child_sync.add_argument("--delete-on-sync", **Args.delete_on_sync)
    child_sync.add_argument("calendar", **Args.calendar)
    child_sync.add_argument("org_file", **Args.orgfile)
    child_sync.set_defaults(func=sync)

    return parent


def _read_static_txt(name: str) -> str:
    path: str = join(paths.static_dir, name)
    with open(path) as file_:
        return file_.read()


class ParserInfo:
    """Constructor arguments for the ArgumentParser objects."""

    parent: dict = dict(
        prog="khalorg",
        formatter_class=RawDescriptionHelpFormatter,
        description="Interface between Khal and Orgmode.",
    )

    new: dict = dict(
        prog="khalorg new",
        formatter_class=RawDescriptionHelpFormatter,
        description=_read_static_txt("description_new_command.txt"),
    )

    list_command: dict = dict(
        formatter_class=RawDescriptionHelpFormatter,
        prog="khalorg list",
        description=_read_static_txt("description_list_command.txt"),
    )

    edit: dict = dict(
        prog="khalorg edit",
        description=_read_static_txt("description_edit_command.txt"),
    )

    delete: dict = dict(
        prog="khalorg delete",
        description=_read_static_txt("description_delete_command.txt"),
    )

    sync: dict = dict(
        formatter_class=RawDescriptionHelpFormatter,
        prog="khalorg sync",
        description=_read_static_txt("description_sync_command.txt"),
    )


class Args:
    """Arguments for the ArgumentParser.add_argument methods."""

    calendar: dict = dict(type=str, help="Set the name of the khal calendar.")
    conflict_resolution: dict = dict(
        type=str,
        help=(
            "What source of truth use in case of conflict "
            "it can be one of: khal, org (default: khal)"
        ),
        default="khal",
    )
    delete_on_sync: dict = dict(
        action="store_true",
        help=(
            "Whether to delete events that disappear from one of the sources "
            "WARNING: if you delete your local file, it will remove all the events "
            "in the remote!!!"
        ),
    )

    loglevel: dict = dict(
        required=False,
        default="WARNING",
        help=(
            "Set the logging level to: CRITICAL, ERROR, WARNING "
            "(default), INFO, DEBUG"
        ),
    )
    logfile: dict = dict(
        type=str, default=paths.log_file, help="The path to the log file."
    )
    orgfile: dict = dict(type=str, help="The path to the org file.")

    start: dict = dict(
        type=str,
        default="today",
        nargs="?",
        help="Start date (default: today)",
    )

    start_sync: dict = dict(
        type=str,
        default="today",
        help="Start date (default: today)",
    )

    state_dir: dict = dict(
        type=str,
        default=paths.state_dir,
        help="The path to the log file.",
    )

    stop: dict = dict(
        type=str, default="1d", nargs="?", help="End date (default: 1d)"
    )
    stop_sync: dict = dict(
        type=str, default="90d", help="End date (default: 90d)"
    )

    format: dict = dict(
        type=str, default=get_khalorg_format(), help="The format of the events."
    )

    edit_dates: dict = dict(
        action="store_true",
        help="Add this flag to also edit the date and its recurrence.",
    )
