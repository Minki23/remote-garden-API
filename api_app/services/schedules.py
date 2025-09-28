from uuid import uuid4
from exceptions.scheme import AppException
from common_db.enums import ScheduleActionType
from repos.schedules import ScheduleRepository


class ScheduleService:
    """
    Service for managing scheduled tasks in the system.
    """

    def __init__(self, repo: ScheduleRepository):
        """
        Initialize the service with a schedule repository.
        """
        self.repo = repo

    def _task_args(self, id: int, action: ScheduleActionType = None) -> list:
        """
        Build task arguments for a scheduled job.

        Parameters
        ----------
        id : int
            Garden ID.
        action : ScheduleActionType, optional
            The action to be executed, if applicable.

        Returns
        -------
        list
            Arguments to pass to the scheduled task.
        """
        if action:
            return [id, action.value]
        return [id]

    def _validate_modifiable(self, task_id: str, is_agent: bool):
        """
        Ensure that a scheduled task can be modified or deleted.

        Parameters
        ----------
        task_id : str
            The ID of the task to validate.
        is_agent : bool
            Whether the modification is performed by an agent.

        Raises
        ------
        AppException
            If the task cannot be modified due to business rules.
        """
        garden_id = self.get_garden_id(task_id)
        tasks = self.repo.list_all(garden_id)
        task = next((t for t in tasks if t["task_id"] == task_id), None)

        if not task:
            raise AppException(f"Task with ID {task_id} not found")

        created_by_ai = task.get("created_by_ai", False)

        if "_agent_" in task_id:
            raise AppException(
                f"Agent task {task_id} cannot be modified or deleted")

        if not is_agent and created_by_ai:
            raise AppException(f"User cannot modify AI-created task {task_id}")

    def list_all(self, garden_id: int) -> list[dict]:
        """
        List all scheduled tasks for a given garden.

        Parameters
        ----------
        garden_id : int
            ID of the garden.

        Returns
        -------
        list of dict
            List of scheduled task definitions.
        """
        return self.repo.list_all(garden_id)

    def create(
        self, garden_id: int, cron: str, action: ScheduleActionType, created_by_ai: bool
    ) -> str:
        """
        Create a new scheduled task for a garden.

        Parameters
        ----------
        garden_id : int
            ID of the garden.
        cron : str
            Cron expression defining the schedule.
        action : ScheduleActionType
            Action to be executed.
        created_by_ai : bool
            Whether the task was created by an AI.

        Returns
        -------
        str
            ID of the created scheduled task.
        """
        task_id = f"garden_{garden_id}_{uuid4().hex}"
        return self.repo.create(
            task_name="schedulers.tasks.run_scheduled_action",
            cron=cron,
            args=self._task_args(garden_id, action),
            task_id=task_id,
            created_by_ai=created_by_ai,
        )

    def create_agent(self, garden_id: int, interval: int) -> str:
        """
        Create a recurring agent task for a garden.

        Parameters
        ----------
        garden_id : int
            ID of the garden.
        interval : int
            Interval in minutes between executions.

        Returns
        -------
        str
            ID of the created agent task.

        Raises
        ------
        AppException
            If the interval is not greater than 0.
        """
        if interval <= 0:
            raise AppException("Interval must be greater than 0")

        task_id = f"garden_{garden_id}_agent_{uuid4().hex}"
        cron = f"*/{interval} * * * *"

        return self.repo.create(
            task_name="schedulers.tasks.trigger_agent",
            cron=cron,
            args=self._task_args(garden_id),
            task_id=task_id,
            created_by_ai=False,
        )

    def update(self, task_id: str, cron: str, is_agent: bool):
        """
        Update the schedule of a task.

        Parameters
        ----------
        task_id : str
            ID of the task to update.
        cron : str
            New cron expression.
        is_agent : bool
            Whether the update is performed by an agent.
        """
        self._validate_modifiable(task_id, is_agent)
        self.repo.update(task_id, cron)

    def delete(self, task_id: str, is_agent: bool):
        """
        Delete a scheduled task.

        Parameters
        ----------
        task_id : str
            ID of the task to delete.
        is_agent : bool
            Whether the deletion is performed by an agent.
        """
        self._validate_modifiable(task_id, is_agent)
        self.repo.delete(task_id)

    def toggle(self, task_id: str, is_agent: bool):
        """
        Toggle the enabled state of a scheduled task.

        Parameters
        ----------
        task_id : str
            ID of the task to toggle.
        is_agent : bool
            Whether the action is performed by an agent.
        """
        self._validate_modifiable(task_id, is_agent)
        self.repo.toggle(task_id)

    def get_garden_id(self, task_id: str) -> int:
        """
        Extract the garden ID from a task ID.

        Parameters
        ----------
        task_id : str
            Task identifier, expected to start with "garden\_".

        Returns
        -------
        int
            The garden ID extracted from the task ID.

        Raises
        ------
        AppException
            If the task ID format is invalid.
        """
        if task_id.startswith("garden_"):
            try:
                return int(task_id.split("_")[1])
            except (IndexError, ValueError):
                raise AppException(f"Invalid task_id format: {task_id}")
        raise AppException(f"Invalid task_id prefix: {task_id}")

    def set_enable(self, garden_id: int, enable: bool) -> list[dict]:
        """
        Enable or disable all agent tasks for a garden.

        Parameters
        ----------
        garden_id : int
            ID of the garden.
        enable : bool
            Whether to enable or disable tasks.

        Returns
        -------
        list of dict
            List of updated agent tasks.

        Raises
        ------
        AppException
            If no agent tasks are found for the garden.
        """
        tasks = self.repo.list_all(garden_id)
        agent_tasks = [t for t in tasks if "_agent_" in t["task_id"]]

        if not agent_tasks:
            raise AppException(f"No agent task found for garden {garden_id}")

        for task in agent_tasks:
            self.repo.set_enabled(task["task_id"], enable)

        return agent_tasks

    def delete_all_ai(self, garden_id: int) -> list[dict]:
        """
        Delete all AI-created tasks for a garden.

        Parameters
        ----------
        garden_id : int
            ID of the garden.

        Returns
        -------
        list of dict
            List of deleted tasks.
        """
        tasks = self.repo.list_all(garden_id)
        ai_tasks = [t for t in tasks if t.get("created_by_ai", False)]

        for task in ai_tasks:
            self.repo.delete(task["task_id"])

        return ai_tasks
