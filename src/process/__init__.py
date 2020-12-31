from celery import Celery

from src.config import Config

processor = Celery(
    "job-processor",
    broker=Config().CELERY_BROKER_URL,
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
)
