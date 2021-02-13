import logging
import sys

from src.config import config


def setup_logging(default_log_level=logging.INFO):
    """Initializes logging."""
    logging_format = (
        "%(asctime)s [%(process)d] [%(levelname)s] "
        "%(module)s::%(funcName)s():l%(lineno)d: "
        "%(message)s"
    )
    logging.basicConfig(
        stream=sys.stdout,
        level=default_log_level,
        format=logging_format,
    )
    logging.getLogger("sanic.root").propagate = False
