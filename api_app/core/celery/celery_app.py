from celery import Celery

celery_app = Celery("garden_scheduler")
celery_app.config_from_object("core.celery.celery_config")
celery_app.autodiscover_tasks(["schedulers.tasks"])
