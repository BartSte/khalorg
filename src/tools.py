import sys
import logging
from os.path import dirname
from inspect import getfile
from types import ModuleType

from orgparse.date import OrgDate
from orgparse.node import OrgNode


def get_module_path(module: ModuleType) -> str:
    """Returns the path to the `module`.

    Args:
        module: a python module

    Returns:
        str: path to module

    """
    return dirname(getfile(module))


class OrgAgendaItem:

    def __init__(self,
                 heading: str,
                 time_stamps: list,
                 scheduled: OrgDate = OrgDate(None),
                 deadline: OrgDate = OrgDate(None),
                 properties: dict = {},
                 body: str = ''):

        self.heading: str = heading
        self.time_stamps: list = time_stamps
        self.scheduled: OrgDate = scheduled
        self.deadline: OrgDate = deadline
        self.properties: dict = properties
        self.body: str = body

    def __eq__(self, other) -> bool:
        try:
            return self.compare(self, other)
        except AttributeError as error:
            message: str = 'Try using a object of type OrgAgendaItem.'
            raise AttributeError(message) from error

    @staticmethod
    def compare(a, b) -> bool:
        return all([getattr(a, x) == getattr(b, x) for x in vars(a)])

    @classmethod
    def from_org_node(cls, node: OrgNode) -> 'OrgAgendaItem':
        child: OrgNode = node.root.children[0]

        kwargs: dict = dict(active=True, inactive=False, range=True, poin=True)
        time_stamps: list = child.get_timestamps(**kwargs)

        return cls(
            child.heading,
            time_stamps=time_stamps,
            scheduled=OrgDate(child.scheduled.start, child.scheduled.end),
            deadline=OrgDate(child.deadline.start, child.deadline.end),
            properties=child.properties,
            body=child.body
        )


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
