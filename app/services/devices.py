from app.exceptions.scheme import AppException
from app.models.enums import ControlActionType, DeviceType
from app.models.dtos.devices import DeviceDTO, DeviceCreateDTO
from app.mappers.devices import db_to_dto
from app.repos.devices import DeviceRepository
from sqlalchemy import select


class DeviceService:
    def __init__(self, repo: DeviceRepository):
        self.repo = repo

    async def get_all(self) -> list[DeviceDTO]:
        devices = await self.repo.get_all()
        return [db_to_dto(d) for d in devices]

    async def get_by_id(self, id: int) -> DeviceDTO:
        device = await self.repo.get_by_id(id)
        return db_to_dto(device)

    async def create(self, dto: DeviceCreateDTO) -> DeviceDTO:
        device = await self.repo.create(garden_id=dto.garden_id, mac=dto.mac, type=dto.type)
        return db_to_dto(device)

    async def delete(self, id: int) -> bool:
        return await self.repo.delete(id)

    async def get_all_for_garden(self, garden_id: int) -> list[DeviceDTO]:
        devices = await self.repo.get_all_by_garden_id(garden_id)
        return [db_to_dto(d) for d in devices]

    async def create_all_for_garden(
        self, garden_id: int, dtos: list[DeviceCreateDTO]
    ) -> list[DeviceDTO]:
        result = []
        for dto in dtos:
            device = await self.repo.create(garden_id=garden_id, mac=dto.mac, type=dto.type)
            result.append(db_to_dto(device))
        return result

    async def _get_garden_device_by_type(self, garden_id: int, type: DeviceType):
        from app.models.db import DeviceDb

        result = await self.repo.db.execute(
            select(DeviceDb).where(DeviceDb.garden_id == garden_id, DeviceDb.type == type)
        )
        device = result.scalars().first()
        if not device:
            raise AppException(
                message=f"No device of type {type} found in garden {garden_id}",
                status_code=404,
            )
        return device

    async def control_device(
        self,
        garden_id: int,
        type: DeviceType,
        action: ControlActionType,
        **kwargs,
    ) -> bool:
        device = await self._get_garden_device_by_type(garden_id, type)

        payload = {
            "action": action.value,
            "device_id": device.id,
            "type": device.type,
            "kwargs": kwargs,
        }

        print(f"[MOCK MQTT] Publishing to device {device.id}: {payload}")
        return True
