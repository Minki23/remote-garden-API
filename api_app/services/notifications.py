from models.dtos.notifications import NotificationDTO, NotificationCreateDTO
from mappers.notifications import db_to_dto
from repos.notifications import NotificationRepository
from fastapi import HTTPException, status


class NotificationService:
    def __init__(self, repo: NotificationRepository):
        self.repo = repo

    async def get_all(self) -> list[NotificationDTO]:
        notifs = await self.repo.get_all()
        return [db_to_dto(n) for n in notifs]

    async def get_by_id(self, id: int) -> NotificationDTO:
        notif = await self.repo.get_by_id(id)
        return db_to_dto(notif)

    async def create(self, dto: NotificationCreateDTO) -> NotificationDTO:
        notif = await self.repo.create(
            user_id=dto.user_id, message=dto.message, read=False, type=dto.type
        )
        return db_to_dto(notif)

    async def delete(self, id: int) -> bool:
        return await self.repo.delete(id)

    async def get_by_user(self, user_id: int) -> list[NotificationDTO]:
        notifs = await self.repo.get_by_user(user_id)
        return [db_to_dto(n) for n in notifs]

    async def dismiss(self, id: int, user_id: int) -> bool:
        notif = await self.repo.get_by_id(id)
        if notif is None or notif.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found"
            )
        return await self.repo.mark_as_read(id)

    async def get_by_user_and_type(
        self, user_id: int, type_: str
    ) -> list[NotificationDTO]:
        notifs = await self.repo.get_by_user_and_type(user_id, type_)
        return [db_to_dto(n) for n in notifs]
