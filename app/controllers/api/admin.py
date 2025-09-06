from fastapi import APIRouter
from app.core.dependencies import AdminUserDep, DeviceServiceDep, EspDeviceServiceDep
from app.models.dtos.admin import CreateEspDeviceRequest

router = APIRouter()


@router.post("/create", status_code=201)
async def create_esp_device(
    data: CreateEspDeviceRequest,
    service: EspDeviceServiceDep,
    device_service: DeviceServiceDep,
    _: AdminUserDep,
):
    device = await service.register_new_device(data.mac, data.secret)
    await device_service.create_all_for_esp(device.id)

    return {"status": "created", "mac": device.mac}
