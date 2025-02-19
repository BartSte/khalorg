from argparse import Namespace

from khalorg import logger
from khalorg.cli import get_parser


def main():
    """Command line interface."""
    args: Namespace = get_parser().parse_args()
    logger.setup(level=args.loglevel, logfile=args.logfile)
    print(args.func(**vars(args)))
