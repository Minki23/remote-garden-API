from app.models.enums import ControlActionType, DeviceType
from fastapi import APIRouter, Body
from app.core.dependencies import DeviceServiceDep, GardenDep
from app.models.dtos.devices import DeviceCreateDTO, DeviceDTO
from app.models.dtos.status import StatusDTO
from app.core.dependencies import StatusServiceDep

router = APIRouter()


@router.get("/{garden_id}", response_model=list[DeviceDTO])
async def get_by_garden(service: DeviceServiceDep, garden: GardenDep):
    return await service.get_all_for_garden(garden.id)


@router.get("/{garden_id}/status", response_model=StatusDTO)
async def get_status(service: StatusServiceDep, garden: GardenDep):
    return await service.get_status(DeviceType.ESP, garden.id)


# Control device endpoints


@router.post("/{garden_id}/light/on", response_model=bool)
async def turn_on_light(service: DeviceServiceDep, garden: GardenDep):
    return await service.control_device(garden.id, DeviceType.LIGHT, ControlActionType.TURN_ON)


@router.post("/{garden_id}/light/off", response_model=bool)
async def turn_off_light(service: DeviceServiceDep, garden: GardenDep):
    return await service.control_device(garden.id, DeviceType.LIGHT, ControlActionType.TURN_OFF)


@router.post("/{garden_id}/water/start", response_model=bool)
async def start_watering(service: DeviceServiceDep, garden: GardenDep):
    return await service.control_device(
        garden.id, DeviceType.WATER_PUMP, ControlActionType.START_WATERING
    )


@router.post("/{garden_id}/roof/open", response_model=bool)
async def open_roof(service: DeviceServiceDep, garden: GardenDep):
    return await service.control_device(garden.id, DeviceType.ROOF, ControlActionType.OPEN_ROOF)


@router.post("/{garden_id}/roof/close", response_model=bool)
async def close_roof(service: DeviceServiceDep, garden: GardenDep):
    return await service.control_device(garden.id, DeviceType.ROOF, ControlActionType.CLOSE_ROOF)


@router.post("/{garden_id}/esp/reset", response_model=bool)
async def reset_esp(service: DeviceServiceDep, garden: GardenDep):
    return await service.control_device(garden.id, DeviceType.ESP, ControlActionType.RESET_ESP)


# @router.post("/{garden_id}/esp/pair", response_model=bool)
# async def pair_esp(service: DeviceServiceDep, garden: GardenDep):
#     return await service.control_device(garden.id, DeviceType.ESP, ControlActionType.PAIR_ESP)


@router.post("/{garden_id}/heater/increase", response_model=bool)
async def increase_temperature(
    service: DeviceServiceDep, garden: GardenDep, amount: int = Body(..., embed=True)
):
    return await service.control_device(
        garden.id, DeviceType.HEATER, ControlActionType.INCREASE_TEMPERATURE, amount=amount
    )


@router.post("/{garden_id}/heater/decrease", response_model=bool)
async def decrease_temperature(
    service: DeviceServiceDep, garden: GardenDep, amount: int = Body(..., embed=True)
):
    return await service.control_device(
        garden.id, DeviceType.HEATER, ControlActionType.DECREASE_TEMPERATURE, amount=amount
    )
