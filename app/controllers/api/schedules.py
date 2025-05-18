from app.models.dtos.schedules import ScheduleCreateDTO
from fastapi import APIRouter, Body
from app.models.enums import ScheduleActionType
from app.core.dependencies import GardenDep, ScheduleServiceDep, UserScheduleDep, WeeklyCronDep

router = APIRouter()


@router.get("/{garden_id}/")
async def list_schedules(garden: GardenDep, service: ScheduleServiceDep):
    return service.list(garden_id=garden.id)


@router.post("/{garden_id}/")
async def create_schedule(
    garden: GardenDep,
    service: ScheduleServiceDep,
    dto: ScheduleCreateDTO,
):
    return {"task_id": service.create(garden.id, dto.cron, dto.action)}


@router.put("/{task_id}/")
async def update_schedule(
    task_id: UserScheduleDep,
    service: ScheduleServiceDep,
    cron: str = Body(...),
):
    service.update(task_id, cron)
    return {"updated": True}


@router.delete("/{task_id}/")
async def delete_schedule(task_id: UserScheduleDep, service: ScheduleServiceDep):
    service.delete(task_id)
    return {"deleted": True}


@router.post("/{task_id}/toggle/")
async def toggle_schedule(task_id: UserScheduleDep, service: ScheduleServiceDep):
    service.toggle(task_id)
    return {"toggled": True}


# similar to the above, but for weekdays instead of cron


@router.post("/weekly/{garden_id}/")
async def create_weekly_schedule(
    garden: GardenDep,
    cron_action: WeeklyCronDep,
    service: ScheduleServiceDep,
):
    return {"task_id": service.create(garden.id, *cron_action)}


@router.put("/weekly/{task_id}/")
async def update_weekly_schedule(
    task_id: UserScheduleDep,
    cron_action: WeeklyCronDep,
    service: ScheduleServiceDep,
):
    cron, _ = cron_action
    service.update(task_id, cron)
    return {"updated": True}
