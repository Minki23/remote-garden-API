from uuid import uuid4
from app.exceptions.scheme import AppException
from app.models.enums import ScheduleActionType
from app.repos.schedules import ScheduleRepository


class ScheduleService:
    def __init__(self, repo: ScheduleRepository):
        self.repo = repo

    def _task_args(self, id: int, action: ScheduleActionType = None):
        if action:
            return [id, action.value]
        return [id]

    def _validate_modifiable(self, task_id: str, is_agent: bool):
        garden_id = self.get_garden_id(task_id)
        tasks = self.repo.list(garden_id)
        task = next((t for t in tasks if t["task_id"] == task_id), None)

        if not task:
            raise AppException(f"Task with ID {task_id} not found")

        created_by_ai = task.get("created_by_ai", False)

        if "_agent_" in task_id:
            raise AppException(
                f"Agent task {task_id} cannot be modified or deleted")

        if is_agent and not created_by_ai:
            raise AppException(
                f"Agent cannot modify user-created task {task_id}")

        if not is_agent and created_by_ai:
            raise AppException(f"User cannot modify AI-created task {task_id}")

    def list(self, garden_id: int):
        return self.repo.list(garden_id)

    def create(self, garden_id: int, cron: str, action: ScheduleActionType, created_by_ai: bool):
        task_id = f"garden_{garden_id}_{uuid4().hex}"
        return self.repo.create(
            task_name="app.schedulers.tasks.run_scheduled_action",
            cron=cron,
            args=self._task_args(garden_id, action),
            task_id=task_id,
            created_by_ai=created_by_ai,
        )

    def create_agent(self, garden_id: int, interval: int):
        if interval <= 0:
            raise AppException("Interval must be greater than 0")

        task_id = f"garden_{garden_id}_agent_{uuid4().hex}"
        cron = f"*/{interval} * * * *"

        return self.repo.create(
            task_name="app.schedulers.tasks.trigger_agent",
            cron=cron,
            args=self._task_args(garden_id),
            task_id=task_id,
            created_by_ai=False,
        )

    def update(self, task_id: str, cron: str, is_agent: bool):
        self._validate_modifiable(task_id, is_agent)
        self.repo.update(task_id, cron)

    def delete(self, task_id: str, is_agent: bool):
        self._validate_modifiable(task_id, is_agent)
        self.repo.delete(task_id)

    def toggle(self, task_id: str, is_agent: bool):
        self._validate_modifiable(task_id, is_agent)
        self.repo.toggle(task_id)

    def get_garden_id(self, task_id: str) -> int:
        if task_id.startswith("garden_"):
            try:
                return int(task_id.split("_")[1])
            except (IndexError, ValueError):
                raise AppException(f"Invalid task_id format: {task_id}")
        raise AppException(f"Invalid task_id prefix: {task_id}")

    def set_enable(self, garden_id: int, enable: bool):
        tasks = self.repo.list(garden_id)
        agent_tasks = [t for t in tasks if "_agent_" in t["task_id"]]

        if not agent_tasks:
            raise AppException(f"No agent task found for garden {garden_id}")

        for task in agent_tasks:
            self.repo.set_enabled(task["task_id"], enable)

        return agent_tasks

    def delete_all_ai(self, garden_id: int):
        tasks = self.repo.list(garden_id)
        ai_tasks = [t for t in tasks if t.get("created_by_ai", False)]

        # if not ai_tasks:
        #     raise AppException(
        #         f"No AI-created tasks found for garden {garden_id}")

        for task in ai_tasks:
            self.repo.delete(task["task_id"])

        return ai_tasks
