#!/usr/bin/env python
import logging
import sys
from typing import Any

import orgparse
from khal.cli import main_khal
from orgparse.node import OrgNode

def main(content: str):
    """

    Args:
    ----
        content (str): 
    """
    org: Any = parse_org_agenda_item(content)
    command: list = get_khal_command(org)
    with TempSysArgv(command) as argv:
        main_khal()


class TempSysArgv:
    """
    The `new` command of khal in not exposed as a function that can easily be called
    from a script. A simpler solution is to temporary change sys.argv so it contains
    the desired command line arguments.

    Attributes 
    ----------
        old: 
        new: 
        argv: 
        argv: 
    """

    def __init__(self, argv: list):
        """

        Args:
            argv (list): 
        """
        self.old: list = sys.argv
        self.new: list = argv

        message: str = f"sys.argv will temporary be replaced by: {argv}"
        logging.info(message)

    def __enter__(self):
        """

        Args:
            self (): 
        """
        sys.argv = self.new
        logging.debug(f'Sys argv is set to: {sys.argv}')
        return self

    def __exit__(self, *_):
        """

        Args:
            self (): 
            *_: 
        """
        sys.argv = self.old
        logging.debug(f'Sys argv is reset to: {sys.argv}')



def get_khal_command(org) -> list:
    """

    Returns
    -------

    """
    return ['khal new', '--help']
