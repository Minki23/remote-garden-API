from fastapi import APIRouter
from core.dependencies import (
    DeviceServiceDep,
    EspDeviceForGardenDep,
    SpecificEspDeviceForGardenDep,
)
from common_db.enums import ControlActionType, DeviceType
from models.dtos.devices import DeviceDTO

router = APIRouter()


@router.get("/garden/{garden_id}", response_model=list[DeviceDTO])
async def get_by_garden(service: DeviceServiceDep, esps: EspDeviceForGardenDep):
    """
    Get all devices in a garden.

    Returns a list of devices associated with the garden’s ESPs.
    """
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


def make_all_handler(device_type: DeviceType, action_type: ControlActionType):
    async def control_all_action(
        service: DeviceServiceDep,
        esps: EspDeviceForGardenDep,
    ):
        """
        Control all ESP devices of type ``{device_type}`` in a garden.

        Executes the specified action across all devices.
        """
        return await service.control_device(esps, device_type, action_type)

    return control_all_action


def make_one_handler(device_type: DeviceType, action_type: ControlActionType):
    async def control_one_action(
        service: DeviceServiceDep,
        esp: SpecificEspDeviceForGardenDep,
    ):
        """
        Control a specific ESP device of type ``{device_type}``.

        Executes the specified action on a single device.
        """
        return await service.control_device([esp], device_type, action_type)

    return control_one_action


for path, (device_type, action_type) in CONTROL_MAP.items():
    router.post(
        f"/garden/{{garden_id}}/{path}",
        response_model=bool,
        name=f"{path.replace('/', '_')}_all",
    )(make_all_handler(device_type, action_type))

    router.post(
        f"/esp/{{esp_id}}/{path}",
        response_model=bool,
        name=f"{path.replace('/', '_')}_one",
    )(make_one_handler(device_type, action_type))
