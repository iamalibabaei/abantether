import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task.settings.development")
app = Celery("django_celery")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


app.conf.beat_schedule = {
    "finalize_transactions_more_than_ten_dollars_task": {
        "task": "finalize_transactions_more_than_ten_dollars",
        "schedule": 1.0,
    },
    "finalize_transactions_less_than_ten_dollars_task": {
        "task": "finalize_transactions_less_than_ten_dollars",
        "schedule": 1.0,
    },
}
