from typing import List
from repos.gardens import GardenRepository
from services.devices import DeviceService
from models.dtos.gardens import (
    GardenDTO,
    GardenCreateDTO,
    GardenPreferencesUpdateDTO,
)


class GardenService:
    """
    Service for managing gardens, including creation, deletion,
    updates, user preferences, and retrieval.
    """

    def __init__(self, repo: GardenRepository, device_service: DeviceService):
        """
        Initialize the service.
        """
        self.repo = repo
        self.device_service = device_service

    async def create_garden(self, dto: GardenCreateDTO, user_id: int) -> GardenDTO:
        """
        Create a new garden for a given user.

        Parameters
        ----------
        dto : GardenCreateDTO
            Data required to create the garden (e.g., name, prefs).
        user_id : int
            ID of the user owning the garden.

        Returns
        -------
        GardenDTO
            Newly created garden as DTO.
        """
        garden = await self.repo.create(user_id=user_id, name=dto.name)
        return GardenDTO(**garden.__dict__)

    async def delete_garden(self, garden_id: int) -> None:
        """
        Delete a garden by its ID.
        """
        await self.repo.delete(garden_id)

    async def update_garden_name(self, garden_id: int, name: str) -> GardenDTO:
        """
        Update the name of a garden.

        Parameters
        ----------
        garden_id : int
            ID of the garden to update.
        name : str
            New name of the garden.

        Returns
        -------
        GardenDTO
            Updated garden as DTO.
        """
        updated = await self.repo.update(garden_id, name=name)
        return GardenDTO(**updated.__dict__)

    async def get_gardens_by_user(self, user_id: int) -> List[GardenDTO]:
        """
        Retrieve all gardens owned by a user.

        Parameters
        ----------
        user_id : int
            ID of the user.

        Returns
        -------
        List[GardenDTO]
            List of gardens belonging to the user.
        """
        gardens = await self.repo.get_all_by_user(user_id)
        return [GardenDTO(**g.__dict__) for g in gardens]

    async def update_preferences(
        self, garden_id: int, prefs: GardenPreferencesUpdateDTO
    ) -> GardenDTO:
        """
        Update garden preferences (notifications, automation, units).

        Parameters
        ----------
        garden_id : int
            ID of the garden to update.
        prefs : GardenPreferencesUpdateDTO
            Preferences DTO with new values.

        Returns
        -------
        GardenDTO
            Updated garden as DTO.
        """
        updated = await self.repo.update(
            garden_id,
            send_notifications=prefs.send_notifications,
            enable_automation=prefs.enable_automation,
            use_fahrenheit=prefs.use_fahrenheit,
        )
        return GardenDTO(**updated.__dict__)
