"""Setup a stream and file logger"""

import logging
from logging.handlers import RotatingFileHandler

from khalorg import paths


def setup(level: int | str = "INFO", logfile: str = paths.log_file):
    """Setup the root logger.

    Args
        level: The level to log at.
        path: The path to the log file.

    Returns
        logger: The root logger.

    """
    level = getattr(logging, level, "INFO") if isinstance(level, str) else level

    logger = logging.getLogger()
    logger.setLevel(level)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    stream = logging.StreamHandler()
    stream.setLevel(level)
    stream.setFormatter(formatter)

    file = RotatingFileHandler(logfile, maxBytes=1 * 1024 * 1024, backupCount=5)
    file.setLevel(level)
    file.setFormatter(formatter)

    logger.addHandler(stream)
    logger.addHandler(file)

    logging.info("--- New run ---")
