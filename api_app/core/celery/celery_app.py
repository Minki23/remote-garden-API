from datetime import timedelta
from celery import Celery

celery_app = Celery("garden_scheduler")
celery_app.config_from_object("app.core.celery.celery_config")
celery_app.autodiscover_tasks(["app.schedulers.tasks"])

# celery_app.conf.beat_schedule = {
#     "demo-log-every-15s": {
#         "task": "app.schedulers.tasks.demo_log",
#         "schedule": timedelta(seconds=15),
#         "args": (),
#     },
# }
