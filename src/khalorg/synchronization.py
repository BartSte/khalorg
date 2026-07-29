"""Implementation helpers for synchronizing org files with khal calendars."""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from khalorg.khal.calendar import Calendar
from khalorg.org.agenda_items import OrgAgendaFile, OrgAgendaItem

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


def load_sync_agenda(path: Path) -> OrgAgendaFile:
    """Load an org agenda without creating a missing file."""
    if path.exists():
        return OrgAgendaFile.from_path(path)
    return OrgAgendaFile.from_str("")


def push_org_changes(
    context: SyncContext,
    edit_dates: bool,
    conflict_resolution: ConflictResolution,
    new_command: SyncCommand,
    edit_command: SyncCommand,
) -> set[str | None]:
    """Push local changes to khal and apply remote updates locally."""
    processed_uids: set[str | None] = set()
    synchronizer = _OrgItemSynchronizer(
        context,
        edit_dates,
        conflict_resolution,
        new_command,
        edit_command,
    )

    for index, item in enumerate(context.org_agenda.items):
        state_item = context.state_agenda.get_item(item.uid)
        khal_item = context.khal_agenda.get_item(item.uid)
        item_processed = synchronizer.sync(
            index,
            item,
            state_item,
            khal_item,
        )
        if item_processed:
            processed_uids.add(item.uid)

    return processed_uids


class _OrgItemSynchronizer:
    """Synchronize individual org items using one run's settings."""

    def __init__(
        self,
        context: SyncContext,
        edit_dates: bool,
        conflict_resolution: ConflictResolution,
        new_command: SyncCommand,
        edit_command: SyncCommand,
    ) -> None:
        """Initialize an item synchronizer."""
        self.context = context
        self.edit_dates = edit_dates
        self.conflict_resolution = conflict_resolution
        self.new_command = new_command
        self.edit_command = edit_command

    def sync(
        self,
        index: int,
        item: OrgAgendaItem,
        state_item: OrgAgendaItem | None,
        khal_item: OrgAgendaItem | None,
    ) -> bool:
        """Synchronize one org item and report whether it was processed."""
        if item == state_item and item.similar(khal_item):
            return True
        if khal_item is None:
            if item != state_item:
                return self._push_new_item(index, item)
            # The element was removed remotely. Deletion is handled later.
            return False
        if item == state_item:
            self._pull_updated_khal_item(index, item, khal_item)
        elif state_item is not None and state_item.similar(khal_item):
            self._push_updated_org_item(item)
        elif not item.similar(khal_item):
            self._resolve_edit_conflict(index, item, khal_item)
        else:
            self._raise_unhandled_sync_state(item, state_item, khal_item)
        return True

    def _push_new_item(
        self,
        index: int,
        item: OrgAgendaItem,
    ) -> bool:
        """Create a new khal event for an org item."""
        logging.info(
            f"[org -> khal {self.context.calendar}] Pushing new event "
            f"{item.uid}: {item.title}"
        )
        if self.context.dry_run:
            return True

        self.new_command(calendar=self.context.calendar, org=str(item))
        try:
            new_item_uid = str(
                self.context.khal_calendar.get_events_no_uid(
                    summary_wanted=item.title,
                    start_wanted=item.timestamps[0].start,
                    end_wanted=item.timestamps[0].end,
                )[0].uid
            )
        except IndexError:
            logging.error(
                "Couldn't find in khal an event that matches title: "
                f"{item.title}, start: {item.timestamps[0].start}, "
                f"end: {item.timestamps[0].end}. Skipping this element."
            )
            return False

        logging.info(f"The new event uid is {new_item_uid}")
        item.properties["UID"] = new_item_uid
        item.properties["CALENDAR"] = self.context.calendar
        self.context.org_agenda.items[index] = item
        return True

    def _pull_updated_khal_item(
        self,
        index: int,
        item: OrgAgendaItem,
        khal_item: OrgAgendaItem,
    ) -> None:
        """Replace an unchanged org item with its updated khal version."""
        logging.info(
            f"[khal {self.context.calendar} -> org] Updating event "
            f"{item.uid}: {item.title}"
        )
        self.context.org_agenda.items[index] = khal_item

    def _push_updated_org_item(self, item: OrgAgendaItem) -> None:
        """Update khal from an org item changed only in the org file."""
        logging.info(
            f"[org -> khal {self.context.calendar}] Updating event "
            f"{item.uid}: {item.title}"
        )
        if not self.context.dry_run:
            self.edit_command(
                calendar=self.context.calendar,
                edit_dates=self.edit_dates,
                org=str(item),
            )

    def _resolve_edit_conflict(
        self,
        index: int,
        item: OrgAgendaItem,
        khal_item: OrgAgendaItem,
    ) -> None:
        """Apply the selected source of truth when both versions changed."""
        if self.conflict_resolution is ConflictResolution.KHAL:
            logging.info(
                f"[khal {self.context.calendar} -> org] Conflict updating "
                f"event {item.uid}: {item.title} following "
                f"conflict_resolution {self.conflict_resolution.value}"
            )
            self.context.org_agenda.items[index] = khal_item
            return

        logging.info(
            f"[org -> khal {self.context.calendar}] Conflict updating event "
            f"{item.uid}: {item.title} following conflict_resolution "
            f"{self.conflict_resolution.value}"
        )
        if not self.context.dry_run:
            self.edit_command(
                calendar=self.context.calendar,
                edit_dates=self.edit_dates,
                org=str(item),
            )

    @staticmethod
    def _raise_unhandled_sync_state(
        item: OrgAgendaItem,
        state_item: OrgAgendaItem | None,
        khal_item: OrgAgendaItem,
    ) -> None:
        """Log and raise for a sync state without defined behavior."""
        logging.info(f"Error syncing item {item}")
        logging.info(f"khal_item is: {khal_item}")
        logging.info(f"state_item is: {state_item}")
        raise NotImplementedError


def pull_khal_changes(
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


def remove_deleted_items(
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


def write_sync_files(
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
