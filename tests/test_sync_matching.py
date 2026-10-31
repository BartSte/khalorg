"""Regression tests for matching org and calendar versions during sync."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from khalorg import paths
from khalorg.commands import _edit, list_command, new, sync
from khalorg.khal.calendar import Calendar
from khalorg.org.agenda_items import OrgAgendaFile
from khalorg.synchronization import (
    ConflictResolution,
    SyncContext,
    push_org_changes,
)
from tests.helpers import CustomCliRunner, get_org_item
from tests.test_commands import get_cli_runner as get_cli_runner
from tests.test_commands import runner as runner


@pytest.fixture(autouse=True)
def default_output_format(monkeypatch, tmp_path: Path):
    """Keep these tests independent of the user's output template."""
    monkeypatch.setattr(paths, "format", str(tmp_path / "missing-format"))


def calendar_files(runner: CustomCliRunner) -> dict[str, bytes]:
    """Return the event files to detect calendar mutations."""
    calendar_dir = Path(str(runner.calendars["one"]))
    return {
        event_file.name: event_file.read_bytes()
        for event_file in calendar_dir.glob("*.ics")
    }


@pytest.mark.parametrize("dry_run", [False, True])
def test_initial_sync_accepts_matching_export(
    runner: CustomCliRunner, tmp_path: Path, dry_run: bool
):
    """An existing matching export must establish state without event edits."""
    new("one", org=str(get_org_item()))
    org_file = tmp_path / "events.org"
    state_dir = tmp_path / "state"
    exported = list_command("one")
    org_file.write_text(exported)
    original_files = calendar_files(runner)

    assert sync("one", org_file, state_dir, dry_run=dry_run) == ""

    assert org_file.read_text() == exported
    assert calendar_files(runner) == original_files
    state_file = state_dir / "one.org"
    if dry_run:
        assert not state_dir.exists()
    else:
        assert state_file.read_text() == exported
        sync("one", org_file, state_dir)
        assert calendar_files(runner) == original_files


@pytest.mark.parametrize("conflict_resolution", ["khal", "org"])
@pytest.mark.parametrize("dry_run", [False, True])
def test_sync_accepts_convergent_edits(
    runner: CustomCliRunner,
    tmp_path: Path,
    conflict_resolution: str,
    dry_run: bool,
):
    """Identical edits on both sides must not cause another calendar write."""
    new("one", org=str(get_org_item()))
    org_file = tmp_path / "events.org"
    state_dir = tmp_path / "state"
    sync("one", org_file, state_dir)
    state_file = state_dir / "one.org"
    previous_state = state_file.read_text()
    item = OrgAgendaFile.from_path(org_file).items[0]
    original_title = item.title
    item.title = "Shared updated title"
    _edit("one", item)
    content = org_file.read_text().replace(original_title, item.title)
    org_file.write_text(content)
    original_files = calendar_files(runner)

    sync(
        "one",
        org_file,
        state_dir,
        conflict_resolution=conflict_resolution,
        dry_run=dry_run,
    )

    assert org_file.read_text() == content
    assert calendar_files(runner) == original_files
    assert state_file.read_text() == (previous_state if dry_run else content)


@pytest.mark.parametrize("conflict_resolution", ["khal", "org"])
def test_initial_sync_keeps_conflict_policy(
    runner: CustomCliRunner, tmp_path: Path, conflict_resolution: str
):
    """Different versions without state must retain the conflict policy."""
    new("one", org=str(get_org_item()))
    org_file = tmp_path / "events.org"
    exported = list_command("one")
    original = OrgAgendaFile.from_str(exported).items[0]
    local_title = "Local updated title"
    org_file.write_text(exported.replace(original.title, local_title))

    sync(
        "one",
        org_file,
        tmp_path / "state",
        conflict_resolution=conflict_resolution,
    )

    expected_title = (
        original.title if conflict_resolution == "khal" else local_title
    )
    local = OrgAgendaFile.from_path(org_file).items[0]
    remote = OrgAgendaFile.from_str(list_command("one")).items[0]
    assert local.title == remote.title == expected_title
    assert local.uid == remote.uid == original.uid
    assert len(calendar_files(runner)) == 1


def test_similar_versions_still_push_pending_org_property_edits():
    """Similarity must not bypass a local-only recurrence end-date edit."""
    initial = (
        "* Meeting\n  <2030-01-01 Tue 10:00-11:00 +1w>\n"
        "  :PROPERTIES:\n  :UID: matching-event\n"
        "  :UNTIL: [2030-02-01 Fri]\n  :END:\n"
    )
    org_agenda = OrgAgendaFile.from_str(
        initial.replace("2030-02-01", "2030-03-01")
    )
    state_agenda = OrgAgendaFile.from_str(initial)
    khal_agenda = OrgAgendaFile.from_str(initial)
    context = SyncContext(
        calendar="one",
        khal_calendar=Mock(spec=Calendar),
        org_agenda=org_agenda,
        state_agenda=state_agenda,
        khal_agenda=khal_agenda,
        dry_run=False,
    )
    new_command = Mock(return_value="")
    edit_command = Mock(return_value="")

    processed = push_org_changes(
        context,
        edit_dates=True,
        conflict_resolution=ConflictResolution.KHAL,
        new_command=new_command,
        edit_command=edit_command,
    )

    assert processed == {"matching-event"}
    new_command.assert_not_called()
    edit_command.assert_called_once()
