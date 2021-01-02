import logging
import sys
from src.config import config


def setup_logging():
    logging_format = (
        "%(asctime)s [%(process)d] [%(levelname)s] "
        "%(module)s::%(funcName)s():l%(lineno)d: "
        "%(message)s"
    )
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.DEBUG if config.DEBUG else logging.INFO,
        format=logging_format,
    )
    logging.getLogger("sanic.root").propagate = False
