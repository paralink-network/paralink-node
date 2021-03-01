from celery import Celery
from celery.signals import setup_logging

from src.config import config

processor = Celery(
    "job-processor",
    broker=config.CELERY_BROKER_URL,
    include=["src.process.collector", "src.process.executor"],
)

processor.conf.update(
    result_expires=3600,
    task_routes={
        "src.process.collector.*": {"queue": "collect"},
        "src.process.executor.*": {"queue": "execute"},
    },
    accept_content=["json"],
    broker_transport_options={
        "max_retries": 3,
        "interval_start": 0,
        "interval_step": 0.2,
        "interval_max": 0.5,
    },
)


@setup_logging.connect
def config_loggers(*args, **kwags):
    from logging.config import dictConfig

    from src.logging import DEFAULT_LOGGING_CONFIG

    dictConfig(DEFAULT_LOGGING_CONFIG)
