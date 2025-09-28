from core.security.deps import SubjectType
from models.dtos.schedules import ScheduleCreateDTO
from fastapi import APIRouter, Body, Response
from core.dependencies import (
    CurrentSubjectDep,
    GardenDep,
    ScheduleServiceDep,
    UserScheduleDep,
    WeeklyCronDep,
)
from fastapi import status

router = APIRouter()


@router.get("/{garden_id}/")
async def list_schedules(garden: GardenDep, service: ScheduleServiceDep, subject: CurrentSubjectDep):
    """
    List all schedules for a specific garden.
    Includes both user-defined and agent-defined tasks.
    """
    return service.list(garden.id)


@router.post("/{garden_id}/")
async def create_schedule(
    garden: GardenDep,
    service: ScheduleServiceDep,
    dto: ScheduleCreateDTO,
    subject: CurrentSubjectDep,
):
    """
    Create a new scheduled task for the garden.
    Supports cron-based timing with defined device actions.
    """
    return {"task_id": service.create(garden.id, dto.cron, dto.action, subject[1] == SubjectType.AGENT)}


@router.put("/{task_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def update_schedule(
    task_id: UserScheduleDep,
    service: ScheduleServiceDep,
    subject: CurrentSubjectDep,
    cron: str = Body(...),
):
    """
    Update an existing schedule with a new cron expression.
    Validates ownership and agent context before applying.
    """
    service.update(task_id, cron, subject[1] == SubjectType.AGENT)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{task_id}/")
async def delete_schedule(task_id: UserScheduleDep, service: ScheduleServiceDep, subject: CurrentSubjectDep,):
    """
    Delete a scheduled task by its identifier.
    Removes it permanently from the schedule registry.
    """
    service.delete(task_id, subject[1] == SubjectType.AGENT)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{task_id}/toggle/")
async def toggle_schedule(task_id: UserScheduleDep, service: ScheduleServiceDep):
    """
    Toggle a schedule’s active state on or off.
    Useful for temporary disabling without deletion.
    """
    service.toggle(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/weekly/{garden_id}/")
async def create_weekly_schedule(
    garden: GardenDep,
    cron_action: WeeklyCronDep,
    service: ScheduleServiceDep,
):
    """
    Create a weekly recurring schedule for a garden.
    Uses weekday rules instead of raw cron strings.
    """
    return {"task_id": service.create(garden.id, *cron_action)}


@router.put("/weekly/{task_id}/")
async def update_weekly_schedule(
    task_id: UserScheduleDep,
    cron_action: WeeklyCronDep,
    service: ScheduleServiceDep,
):
    """
    Update a weekly schedule with new weekday rules.
    Keeps the assigned action but adjusts the timing.
    """
    cron, _ = cron_action
    service.update(task_id, cron)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
