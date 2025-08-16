from fastapi import APIRouter
from app.core.dependencies import (
    DeviceServiceDep,
    EspDeviceForGardenDep,
    SpecificEspDeviceForGardenDep,
)
from app.models.enums import ControlActionType, DeviceType
from app.models.dtos.devices import DeviceDTO

router = APIRouter()


@router.get("/garden/{garden_id}", response_model=list[DeviceDTO])
async def get_by_garden(service: DeviceServiceDep, esps: EspDeviceForGardenDep):
    return await service.get_all_for_esps(esps)


CONTROL_MAP = {
    "water/on": (DeviceType.WATERER, ControlActionType.WATER_ON),
    "water/off": (DeviceType.WATERER, ControlActionType.WATER_OFF),
    "atomizer/on": (DeviceType.ATOMIZER, ControlActionType.ATOMIZE_ON),
    "atomizer/off": (DeviceType.ATOMIZER, ControlActionType.ATOMIZE_OFF),
    "fan/on": (DeviceType.FANNER, ControlActionType.FAN_ON),
    "fan/off": (DeviceType.FANNER, ControlActionType.FAN_OFF),
    "heating-mat/on": (DeviceType.HEATER, ControlActionType.HEATING_MAT_ON),
    "heating-mat/off": (DeviceType.HEATER, ControlActionType.HEATING_MAT_OFF),
}

for path, (device_type, action_type) in CONTROL_MAP.items():

    @router.post(
        f"/garden/{{garden_id}}/{path}",
        response_model=bool,
        name=f"{path.replace('/', '_')}_all",
    )
    async def control_all_action(
        service: DeviceServiceDep,
        esps: EspDeviceForGardenDep,
        device_type=device_type,
        action_type=action_type,
    ):
        return await service.control_device(esps, device_type, action_type)

    @router.post(
        f"/esp/{{esp_id}}/{path}",
        response_model=bool,
        name=f"{path.replace('/', '_')}_one",
    )
    async def control_one_action(
        service: DeviceServiceDep,
        esp: SpecificEspDeviceForGardenDep,
        device_type=device_type,
        action_type=action_type,
    ):
        return await service.control_device([esp], device_type, action_type)
