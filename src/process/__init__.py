from celery import Celery

processor = Celery(
    "job-processor",
    broker="amqp://localhost",
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
