import json
from app.exceptions.scheme import AppException
import redis
from typing import List
from redbeat import RedBeatSchedulerEntry
from celery.schedules import crontab
from app.core.celery.celery_app import celery_app


class ScheduleRepository:
    def __init__(self):
        self.redis_client = redis.StrictRedis.from_url(
            celery_app.conf.redbeat_redis_url
        )

    def list(self, garden_id: int) -> List[dict]:
        keys = self.redis_client.keys(f"redbeat:garden_{garden_id}_*")
        result = []
        for key in keys:
            data = self.redis_client.hget(key, "definition")
            if data is None:
                continue
            definition = json.loads(data)

            result.append(
                {
                    "task_id": definition["name"],
                    "enabled": definition.get("enabled", True),
                    "cron": definition.get("schedule", {}),
                    "args": definition.get("args", []),
                    "task": definition.get("task", None),
                }
            )
        return result

    def create(self, task_name: str, cron: str, args: list, task_id: str) -> str:
        entry = RedBeatSchedulerEntry(
            name=task_id,
            task=task_name,
            schedule=crontab_from_string(cron),
            args=args,
            app=celery_app,
            enabled=True,
        )
        entry.save()
        return entry.name

    def delete(self, task_id: str):
        key = f"redbeat:{task_id}"
        if not self.redis_client.exists(key):
            raise AppException(
                f"Task with ID {task_id} does not exist in the schedule."
            )
        self.redis_client.delete(key)

    def update(self, task_id: str, cron: str):
        key = f"redbeat:{task_id}"
        if not self.redis_client.exists(key):
            raise AppException(
                f"Task with ID {task_id} does not exist in the schedule."
            )
        entry = RedBeatSchedulerEntry.from_key(key, app=celery_app)
        entry.schedule = crontab_from_string(cron)
        entry.save()

    def toggle(self, task_id: str):
        key = f"redbeat:{task_id}"
        if not self.redis_client.exists(key):
            raise AppException(
                f"Task with ID {task_id} does not exist in the schedule."
            )
        entry = RedBeatSchedulerEntry.from_key(key, app=celery_app)
        entry.enabled = not entry.enabled
        entry.save()


def crontab_from_string(cron: str):
    parts = cron.split()
    return crontab(
        minute=parts[0],
        hour=parts[1],
        day_of_month=parts[2],
        month_of_year=parts[3],
        day_of_week=parts[4],
    )
