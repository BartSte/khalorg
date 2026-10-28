"""Exercise output templates through the real CLI command dispatch."""

from pathlib import Path

import pytest

from khalorg.cli import Args, get_parser
from khalorg.commands import _new
from khalorg.helpers import get_default_khalorg_format
from khalorg.org.agenda_items import OrgAgendaFile, OrgAgendaItem
from tests.helpers import get_org_item
from tests.test_commands import get_cli_runner as get_cli_runner
from tests.test_commands import runner as runner


@pytest.fixture
def calendar_item(runner) -> OrgAgendaItem:
    """Create a calendar event for the command to export."""
    item = get_org_item()
    _new("one", item)
    return item


@pytest.mark.parametrize("explicit_format", [False, True])
def test_list_uses_cli_format(calendar_item, monkeypatch, explicit_format):
    """List must render the explicit or default template from the parser."""
    template = "Title: {title}\nLocation: {location}"
    arguments = ["list", "one", "today", "3d"]
    if explicit_format:
        arguments.extend(["--format", template])
    else:
        monkeypatch.setitem(Args.format, "default", template)
    args = get_parser().parse_args(arguments)

    output = args.func(**vars(args))

    assert output == (
        f"Title: {calendar_item.title}\n"
        f"Location: {calendar_item.properties['LOCATION']}"
    )


@pytest.mark.parametrize("explicit_format", [False, True])
def test_sync_uses_cli_format(
    calendar_item, tmp_path: Path, monkeypatch, explicit_format
):
    """Sync must use the CLI template for both the org file and its state."""
    template = get_default_khalorg_format().replace(
        "* {title}", "** {title}", 1
    )
    org_file = tmp_path / "events.org"
    state_dir = tmp_path / "state"
    arguments = [
        "sync",
        "--state-dir",
        str(state_dir),
        "--stop",
        "3d",
        "one",
        str(org_file),
    ]
    if explicit_format:
        arguments.extend(["--format", template])
    else:
        monkeypatch.setitem(Args.format, "default", template)
    args = get_parser().parse_args(arguments)

    assert args.func(**vars(args)) == ""

    content = org_file.read_text()
    assert content.startswith(f"** {calendar_item.title}\n")
    assert (state_dir / "one.org").read_text() == content
    items = OrgAgendaFile.from_str(content).items
    assert len(items) == 1
    assert items[0].uid
