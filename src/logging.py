import logging.config
import sys

from rich.logging import RichHandler

from src.config import config

DEFAULT_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "loggers": {
        "": {"level": config.LOG_LEVEL, "handlers": ["console"]},
        "sanic.root": {
            "level": "INFO",
            "handlers": ["console"],
            "propagate": False,
        },
        "sanic.error": {
            "level": config.LOG_LEVEL,
            "handlers": ["sanic_error_console"],
            "qualname": "sanic.error",
            "propagate": False,
        },
        "sanic.access": {
            "level": config.LOG_LEVEL,
            "handlers": ["sanic_access_console"],
            "qualname": "sanic.access",
            "propagate": False,
        },
    },
    "handlers": {
        "console": {
            "class": "rich.logging.RichHandler",
            "markup": True,
            "rich_tracebacks": True,
            "formatter": "rich",
        },
        "sanic_root_console": {
            "class": "rich.logging.RichHandler",
            "markup": True,
            "rich_tracebacks": True,
            "formatter": "rich",
        },
        "sanic_error_console": {
            "class": "rich.logging.RichHandler",
            "markup": True,
            "rich_tracebacks": True,
            "formatter": "rich",
        },
        "sanic_access_console": {
            "class": "rich.logging.RichHandler",
            "markup": True,
            "rich_tracebacks": True,
            "formatter": "access",
        },
    },
    "formatters": {
        "rich": {"format": "%(message)s", "datefmt": "[%X]"},
        "access": {
            "format": "[%(host)s]: %(request)s %(message)s %(status)d %(byte)d",
            "datefmt": "[%X]",
        },
    },
}


def setup_logging():
    """Initializes logging."""
    logging.config.dictConfig(DEFAULT_LOGGING_CONFIG)
