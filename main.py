import logging
import sys

from src.org_to_khal import main

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main(sys.stdin.read())
