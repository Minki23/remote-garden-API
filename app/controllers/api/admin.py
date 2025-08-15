from fastapi import APIRouter
from app.core.dependencies import AdminUserDep, EspDeviceServiceDep
from app.models.dtos.admin import CreateEspDeviceRequest

router = APIRouter(prefix="/esp", tags=["Device provisioning"])


@router.post("/create", status_code=201)
async def create_esp_device(
    data: CreateEspDeviceRequest,
    service: EspDeviceServiceDep,
    _=AdminUserDep,
):
    device = await service.register_new_device(data.mac, data.secret)
    return {"status": "created", "mac": device.mac}
