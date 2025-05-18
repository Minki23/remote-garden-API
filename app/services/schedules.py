from uuid import uuid4
from app.models.enums import ScheduleActionType
from app.repos.schedules import ScheduleRepository


class ScheduleService:
    def __init__(self, repo: ScheduleRepository):
        self.repo = repo

    def _task_args(self, garden_id: int, action: ScheduleActionType):
        return [garden_id, action.value]

    def _task_name(self):
        return "app.schedulers.tasks.run_scheduled_action"

    def list(self, garden_id: int):
        return self.repo.list(garden_id)

    def create(self, garden_id: int, cron: str, action: ScheduleActionType):
        task_id = f"garden_{garden_id}_{uuid4().hex}"
        return self.repo.create(
            task_name=self._task_name(),
            cron=cron,
            args=self._task_args(garden_id, action),
            task_id=task_id,
        )

    def update(self, task_id: str, cron: str):
        self.repo.update(task_id, cron)

    def delete(self, task_id: str):
        self.repo.delete(task_id)

    def toggle(self, task_id: str):
        self.repo.toggle(task_id)

    def get_garden_id(self, task_id: str) -> int:
        if task_id.startswith("garden_"):
            try:
                return int(task_id.split("_")[1])
            except (IndexError, ValueError):
                raise ValueError(f"Invalid task_id format: {task_id}")
        raise ValueError(f"Invalid task_id prefix: {task_id}")
