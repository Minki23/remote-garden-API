from fastapi import APIRouter
from app.core.dependencies import CurrentUserDep, UserDeviceServiceDep
from app.models.dtos.user_devices import RegisterDeviceDTO, RemoveDeviceDTO

router = APIRouter()


@router.post("/register/")
async def register_device(
    req: RegisterDeviceDTO,
    user_id: CurrentUserDep,
    service: UserDeviceServiceDep,
):
    device = await service.register_device(
        user_id=user_id, fcm_token=req.fcm_token, platform=req.platform
    )
    return {"registered": True, "device_id": device.id}


@router.post("/remove/")
async def remove_device(
    req: RemoveDeviceDTO,
    service: UserDeviceServiceDep,
):
    removed = await service.remove_device(req.fcm_token)
    return {"removed": removed}
