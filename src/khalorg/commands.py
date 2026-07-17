import logging
import sys
from pathlib import Path

from khalorg.helpers import get_khalorg_format
from khalorg.khal.args import DeleteArgs, EditArgs, KhalArgs, NewArgs
from khalorg.khal.calendar import Calendar, CalendarProperties
from khalorg.khal.checker import EventChecker, EventChecks
from khalorg.khal.helpers import get_khal_format
from khalorg.org.agenda_items import (
    OrgAgendaFile,
    OrgAgendaItem,
)
from khalorg.synchronization import (
    ConflictResolution,
    SyncContext,
    load_sync_agenda,
    pull_khal_changes,
    push_org_changes,
    remove_deleted_items,
    write_sync_files,
)


def list_command(
    calendar: str,
    khalorg_format: str | None = None,
    start: str = "today",
    stop: str = "1d",
    **_,
) -> str:
    """
    Lists khal agenda items to org format.

    Args:
    ----
        calendar: name of the khal calendar
        start: start date (default: today)
        stop: end date (default: 1d)

    Returns
    -------
        stdout of the `khal list` command after post processing

    """
    khalorg_format = khalorg_format or get_khalorg_format()
    agenda = _list(calendar=calendar, start=start, stop=stop)
    return format(agenda, khalorg_format)


def _list(
    calendar: str,
    start: str = "today",
    stop: str = "1d",
    **_,
) -> OrgAgendaFile:
    """
    Lists khal agenda items to OrgAgendaFile.

    Args:
    ----
        calendar: name of the khal calendar
        start: start date (default: today)
        stop: end date (default: 1d)

    Returns
    -------
        List of OrgAgendaFile

    """
    args: KhalArgs = KhalArgs()
    args["-a"] = calendar
    args["-f"] = get_khal_format()
    args["start"] = start
    args["stop"] = stop

    khal_calendar: Calendar = Calendar(calendar)
    org_items: str = khal_calendar.list_command(args.as_list())
    agenda: OrgAgendaFile = OrgAgendaFile.from_str(org_items)
    agenda.apply_rrules()
    return agenda


def new(calendar: str, **kwargs) -> str:
    """
    Creates a new calendar item in a Khal calendar.

    It does this, by parsing an org agenda item, that is supplied through
    stdin, into a list of command line arguments. These arguments are used to
    invoke the `khal new` command by calling Calendar.new_item. Alternatively,
    the org item can be supplied through the keyword arg `org`. The command
    line interface of khal (i.e., `khal new`) was used instead of using the
    underlying functions, because these functions are not readily exposed.
    Furthermore, by using the command line interface, the `khalorg new` command
    is more resilient against changes in the khal api.

    After running the `khal new` command, properties are added to the event
    using the Calendar.edit command. These properties cannot be added through
    the `khal new` command, so this is a workaround.

    Args:
    ----
        calendar: name of the khal calendar.
        until: Stop an event repeating on this date.
        org: omit the stdin and send the input as an argument

    Returns
    -------
        stdout of the `khal new` command

    """
    org = kwargs.get("org", "") or sys.stdin.read()

    checker: EventChecker = EventChecker()
    checker.remove(EventChecks.UID)

    agenda_item: OrgAgendaItem = OrgAgendaItem()
    agenda_item.load_from_str(org)
    agenda_item.properties["UID"] = ""  # UID must be empty for new item

    message: str = checker.is_valid(calendar, agenda_item)
    if not message:
        stdout: str = _new(calendar, agenda_item)
        _edit(calendar, agenda_item, edit_dates=True)
        return stdout
    else:
        logging.critical(message)
        return ""


def _new(calendar: str, agenda_item: OrgAgendaItem) -> str:
    """
    Adds `agenda_item` as an agenda item in khal `calendar`.

    Calendar.new_item calls `khal new` where its command line argument are
    extracted from `agenda_item` by NewArgs.

    Args:
    ----
        calendar: the name of the khal calendar
        agenda_item: org agenda item

    Returns
    -------
       stdout of `khal new`.
    """
    khal_calendar: Calendar = Calendar(calendar)

    args: NewArgs = NewArgs()
    args["-a"] = calendar
    args.load_from_org(agenda_item)
    logging.debug(f"Khal new args are: {args.as_list()}")

    return khal_calendar.new_item(args.as_list())


def edit(calendar: str, edit_dates: bool = False, **kwargs) -> str:
    """
    Edit an existing khal agenda item.

    An existing khal agenda item is edited by supplying an org file with the
    desired properties. Empty fields are interpreted as being actual empty and
    are thus not ignored.

    The org file can be supplied through stdin or through the `org` keyword
    argument.

    Ensure the correct UID is available in the UID properties otherwise the
    corresponding event cannot be found.

    Args:
    ----
        calendar: the name of the calendar.
        edit_dates: If set to True, the org time stamp and its recurrence are
        also edited.
        **_:
    """
    org = kwargs.get("org", "") or sys.stdin.read()

    checker: EventChecker = EventChecker()
    checker.remove(EventChecks.DUPLICATE)

    agenda_item: OrgAgendaItem = OrgAgendaItem()
    agenda_item.load_from_str(org)

    message: str = checker.is_valid(calendar, agenda_item)
    if not message:
        return _edit(calendar, agenda_item, edit_dates)
    else:
        logging.critical(message)
        return ""


def _edit(
    calendar: str, agenda_item: OrgAgendaItem, edit_dates: bool = False
) -> str:
    """
    Edits `agenda_item` that corresponds to an existing agenda item in a
    khal `calendar`.

    Calendar.edit f

    Args:
    ----
        calendar: the name of the khal calendar
        agenda_item: org agenda item
        edit_dates: If set to True, the org time stamp and its recurrence are
        also edited.

    Returns
    -------
       stdout of `khal new`.
    """
    khal_calendar: Calendar = Calendar(calendar)

    args: EditArgs = EditArgs()
    args.load_from_org(agenda_item)
    khal_calendar.edit(CalendarProperties(**args), edit_dates)
    return ""


def delete(calendar: str, **kwargs) -> str:
    """TODO

    Args:
        calendar:
        **kwargs:

    Returns:

    """
    org = kwargs.get("org", "") or sys.stdin.read()

    checker: EventChecker = EventChecker([EventChecks.UID])
    agenda_item: OrgAgendaItem = OrgAgendaItem()
    agenda_item.load_from_str(org)

    message: str = checker.is_valid(calendar, agenda_item)
    if not message:
        return _delete(calendar, agenda_item)
    else:
        logging.critical(message)
        return ""


def _delete(calendar: str, agenda_item: OrgAgendaItem) -> str:
    """TODO.

    Args:
        calendar:
        agenda_item:

    Returns
    -------

    """
    args: DeleteArgs = DeleteArgs()
    args.load_from_org(agenda_item)
    khal_calendar: Calendar = Calendar(calendar)
    return khal_calendar.delete(CalendarProperties(**args))


def sync(
    calendar: str,
    org_file: Path,
    state_dir: Path,
    start: str = "today",
    stop: str = "90d",
    edit_dates: bool = False,
    conflict_resolution: ConflictResolution | str = ConflictResolution.KHAL,
    delete_on_sync: bool = False,
    dry_run: bool = False,
    filetags: list[str] | None = None,
    khalorg_format: str | None = None,
    **_,
) -> str:
    """
    Syncs events between a khal calendar and an org file.

    Args:
    ----
        calendar: name of the khal calendar
        org_file: path to the org file
        start: start date (default: today)
        stop: end date (default: 1d)
        edit_dates: If set to True, the org time stamp and its recurrence are
            also edited.
        conflict_resolution: what source of truth use in case of conflict
            it can be one of: khal, org
        delete_on_sync: Whether to delete events that disappear from one of
            the sources. WARNING: if you delete your local file, it will
            remove all the events in the remote!!!
        dry_run: Doesn't do any action, it just prints what it would do

    Returns
    -------
    empty string

    """
    try:
        conflict_resolution = ConflictResolution(conflict_resolution)
    except ValueError as error:
        raise ValueError(
            f"The value {conflict_resolution} of conflict resolution is not "
            "valid, please use khal or org"
        ) from error

    khal_calendar = Calendar(calendar)
    sync_format: str = khalorg_format or get_khalorg_format()
    state_file = state_dir / f"{calendar}.org"
    filetags = filetags or []

    org_agenda = load_sync_agenda(org_file)
    state_agenda = load_sync_agenda(state_file)
    khal_agenda = _list(calendar=calendar, start=start, stop=stop)
    context = SyncContext(
        calendar=calendar,
        khal_calendar=khal_calendar,
        org_agenda=org_agenda,
        state_agenda=state_agenda,
        khal_agenda=khal_agenda,
        dry_run=dry_run,
    )
    processed_uids = push_org_changes(
        context=context,
        edit_dates=edit_dates,
        conflict_resolution=conflict_resolution,
        new_command=new,
        edit_command=edit,
    )
    pull_khal_changes(
        context=context,
        processed_uids=processed_uids,
    )
    if delete_on_sync:
        remove_deleted_items(
            context=context,
            processed_uids=processed_uids,
            delete_command=delete,
        )
    if not dry_run:
        write_sync_files(
            org_file=org_file,
            state_file=state_file,
            org_agenda=org_agenda,
            khalorg_format=sync_format,
            filetags=filetags,
        )

    # return empty string so that nothing is shown in the CLI
    return ""
