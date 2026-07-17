"""Implementation helpers for synchronizing org files with khal calendars."""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from khalorg.khal.calendar import Calendar
from khalorg.org.agenda_items import OrgAgendaFile

SyncCommand = Callable[..., str]


class ConflictResolution(str, Enum):
    """Source of truth used when both sync targets changed."""

    KHAL = "khal"
    ORG = "org"


@dataclass(frozen=True)
class SyncContext:
    """Shared state used throughout a synchronization run."""

    calendar: str
    khal_calendar: Calendar
    org_agenda: OrgAgendaFile
    state_agenda: OrgAgendaFile
    khal_agenda: OrgAgendaFile
    dry_run: bool


def _load_sync_agenda(path: Path) -> OrgAgendaFile:
    """Load an org agenda without creating a missing file."""
    if path.exists():
        return OrgAgendaFile.from_path(path)
    return OrgAgendaFile.from_str("")


def _push_org_changes(
    context: SyncContext,
    edit_dates: bool,
    conflict_resolution: ConflictResolution,
    new_command: SyncCommand,
    edit_command: SyncCommand,
) -> set[str | None]:
    """Push local changes to khal and apply remote updates locally."""
    processed_uids: set[str | None] = set()

    for index, item in enumerate(context.org_agenda.items):
        state_item = context.state_agenda.get_item(item.uid)
        khal_item = context.khal_agenda.get_item(item.uid)

        if item == state_item and item.similar(khal_item):
            processed_uids.add(item.uid)
            continue
        if khal_item is None and item != state_item:
            logging.info(
                f"[org -> khal {context.calendar}] Pushing new event "
                f"{item.uid}: {item.title}"
            )
            if not context.dry_run:
                new_command(calendar=context.calendar, org=str(item))
                try:
                    new_item_uid = str(
                        context.khal_calendar.get_events_no_uid(
                            summary_wanted=item.title,
                            start_wanted=item.timestamps[0].start,
                            end_wanted=item.timestamps[0].end,
                        )[0].uid
                    )
                except IndexError:
                    logging.error(
                        "Couldn't find in khal an event that matches title: "
                        f"{item.title}, start: {item.timestamps[0].start}, "
                        f"end: {item.timestamps[0].end}. Skipping this "
                        "element."
                    )
                    continue
                logging.info(f"The new event uid is {new_item_uid}")
                item.properties["UID"] = new_item_uid
                item.properties["CALENDAR"] = context.calendar
                context.org_agenda.items[index] = item
        elif khal_item is None and item == state_item:
            # The element was removed remotely. Deletion is handled later.
            continue
        elif (
            khal_item is not None
            and item == state_item
            and not item.similar(khal_item)
        ):
            logging.info(
                f"[khal {context.calendar} -> org] Updating event "
                f"{item.uid}: {item.title}"
            )
            context.org_agenda.items[index] = khal_item
        elif state_item is not None and state_item.similar(khal_item):
            logging.info(
                f"[org -> khal {context.calendar}] Updating event "
                f"{item.uid}: {item.title}"
            )
            if not context.dry_run:
                edit_command(
                    calendar=context.calendar,
                    edit_dates=edit_dates,
                    org=str(item),
                )
        elif khal_item is not None and not item.similar(khal_item):
            if conflict_resolution is ConflictResolution.KHAL:
                logging.info(
                    f"[khal {context.calendar} -> org] Conflict updating "
                    "event "
                    f"{item.uid}: {item.title} following "
                    f"conflict_resolution {conflict_resolution.value}"
                )
                context.org_agenda.items[index] = khal_item
            else:
                logging.info(
                    f"[org -> khal {context.calendar}] Conflict updating "
                    "event "
                    f"{item.uid}: {item.title} following "
                    f"conflict_resolution {conflict_resolution.value}"
                )
                if not context.dry_run:
                    edit_command(
                        calendar=context.calendar,
                        edit_dates=edit_dates,
                        org=str(item),
                    )
        else:
            logging.info(f"Error syncing item {item}")
            logging.info(f"khal_item is: {khal_item}")
            logging.info(f"state_item is: {state_item}")
            raise NotImplementedError
        processed_uids.add(item.uid)

    return processed_uids


def _pull_khal_changes(
    context: SyncContext,
    processed_uids: set[str | None],
) -> None:
    """Add previously unseen khal events to the local agenda."""
    for item in context.khal_agenda.items:
        if item.uid in processed_uids:
            continue
        org_item = context.org_agenda.get_item(item.uid)
        state_item = context.state_agenda.get_item(item.uid)

        if org_item is None and not item.similar(state_item):
            logging.info(
                f"[khal {context.calendar} -> org] Pushing new event "
                f"{item.uid}: {item.title}"
            )
            context.org_agenda.items.append(item)


def _remove_deleted_items(
    context: SyncContext,
    processed_uids: set[str | None],
    delete_command: SyncCommand,
) -> None:
    """Propagate events deleted from either sync target."""
    for item in context.state_agenda.items:
        if item.uid in processed_uids:
            continue

        khal_item = context.khal_agenda.get_item(item.uid)
        org_item = context.org_agenda.get_item(item.uid)
        if item.similar(khal_item) and org_item is None:
            logging.info(
                f"[org -> khal {context.calendar}] Removing deleted event "
                f"{item.uid}: {item.title}"
            )
            if not context.dry_run:
                delete_command(context.calendar, org=str(item))
        elif item == org_item and khal_item is None:
            logging.info(
                f"[khal {context.calendar} -> org] Removing deleted event "
                f"{item.uid}: {item.title}"
            )
            context.org_agenda.items.remove(item)


def _write_sync_files(
    org_file: Path,
    state_file: Path,
    org_agenda: OrgAgendaFile,
    khalorg_format: str,
    filetags: list[str],
) -> None:
    """Persist the synchronized agenda and its state snapshot."""
    state_file.parent.mkdir(parents=True, exist_ok=True)
    if filetags:
        content = f"#+FILETAGS: :{':'.join(filetags)}:\n"
    else:
        content = ""
    content += format(org_agenda, khalorg_format)
    org_file.write_text(content)
    state_file.write_text(content)
