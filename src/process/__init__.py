from celery import Celery

from src.config import config
from src.network import accounts

accounts.load()

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
    task_serializer="pickle",
    accept_content=["json", "pickle"],
    broker_transport_options={
        "max_retries": 3,
        "interval_start": 0,
        "interval_step": 0.2,
        "interval_max": 0.5,
    },
)
