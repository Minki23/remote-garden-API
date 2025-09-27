from fastapi import APIRouter
from core.dependencies import AdminUserDep, DeviceServiceDep, EspDeviceServiceDep
from models.dtos.admin import CreateEspDeviceRequest

router = APIRouter()


@router.post("/esp/create", status_code=201)
async def create_esp_device(
    data: CreateEspDeviceRequest,
    service: EspDeviceServiceDep,
    device_service: DeviceServiceDep,
    _: AdminUserDep,
):
    """
    Register a new ESP device (admin-only).

    Creates an ESP device using the given MAC and secret,
    then provisions its default sensors/actuators.
    """
    device = await service.register_new_device(data.mac, data.secret)
    await device_service.create_all_for_esp(device.id)

    return {"status": "created", "mac": device.mac}
