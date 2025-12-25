import os
from datetime import datetime

from celery import Celery
from celery.schedules import crontab

from core.config import settings

broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
backend_url = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery(
    'cinematch_tasks',
    broker=broker_url,
    backend=backend_url,
    include=['worker.tasks']
)
def get_dynamic_range():
    # Например, в четные дни качаем страницы 10-20, в нечетные 20-30
    day = datetime.now().day
    if day % 2 == 0:
        return (10, 20)
    return (20, 30)

celery_app.conf.beat_schedule = {
    'import-daily-top': {
        'task': 'worker.tasks.initial_load',
        'schedule': crontab(minute=6, hour=0),
        'args': (1, 5),
    },
    'import-deep-archive': {
        'task': 'worker.tasks.initial_load',
        'schedule': crontab(day_of_week='sun', hour=3, minute=0),
        'args': (50, 100),
    },
    'update-day-deep': {
        'task': 'worker.tasks.initial_load',
        'schedule': crontab(minute=0, hour='*/4'),
        'kwargs': {'start_page': 6, 'end_page': 15},
    },
}