import logging
from argparse import Namespace

from khalorg.cli import get_parser


def main():
    """ Command line interface. """
    args: Namespace = get_parser().parse_args()
    logging.basicConfig(level=args.loglevel)
    print(args.func(**vars(args)))
