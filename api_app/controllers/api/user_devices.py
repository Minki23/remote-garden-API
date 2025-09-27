from fastapi import APIRouter
from core.dependencies import CurrentUserDep, UserDeviceServiceDep
from models.dtos.user_devices import RegisterDeviceDTO, RemoveDeviceDTO

router = APIRouter()


@router.post("/register/")
async def register_device(
    req: RegisterDeviceDTO,
    user_id: CurrentUserDep,
    service: UserDeviceServiceDep,
):
    """
    Register a new user device for push notifications.
    Links the device to the current user account.
    """
    device = await service.register_device(
        user_id=user_id, fcm_token=req.fcm_token, platform=req.platform
    )
    return {"registered": True, "device_id": device.id}


@router.post("/remove/")
async def remove_device(
    req: RemoveDeviceDTO,
    service: UserDeviceServiceDep,
):
    """
    Remove a previously registered user device.
    Uses the FCM token to identify the device record.
    """
    removed = await service.remove_device(req.fcm_token)
    return {"removed": removed}
