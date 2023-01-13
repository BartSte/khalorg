#!/usr/bin/env python
import logging
import sys
from typing import Any

import orgparse
from khal.cli import main_khal
from orgparse.node import OrgNode

from src.tools import OrgAgendaItem, TempSysArgv


def main():
    """

    Args:
    ----
        content (str):
    """

    node: OrgNode = orgparse.loads(sys.stdin.read())
    agenda_item: OrgAgendaItem = OrgAgendaItem.from_org_node(node)
    command: list = get_khal_command(agenda_item)
    with TempSysArgv(command) as argv:
        main_khal()


def get_khal_command(org) -> list:
    """

    Returns
    -------

    """
    return ['khal new', '--help']
