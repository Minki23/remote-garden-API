from models.dtos.notifications import NotificationDTO, NotificationCreateDTO
from mappers.notifications import db_to_dto
from repos.notifications import NotificationRepository
from fastapi import HTTPException, status


class NotificationService:
    """
    Service for managing notifications: creation, retrieval, deletion,
    and marking as read.
    """

    def __init__(self, repo: NotificationRepository):
        """
        Initialize the service.
        """
        self.repo = repo

    async def get_all(self) -> list[NotificationDTO]:
        """
        Retrieve all notifications.

        Returns
        -------
        list[NotificationDTO]
            All notifications in the system.
        """
        notifs = await self.repo.get_all()
        return [db_to_dto(n) for n in notifs]

    async def get_by_id(self, id: int) -> NotificationDTO:
        """
        Retrieve a notification by its ID.

        Parameters
        ----------
        id : int
            Notification ID.

        Returns
        -------
        NotificationDTO
            Notification as DTO.
        """
        notif = await self.repo.get_by_id(id)
        return db_to_dto(notif)

    async def create(self, dto: NotificationCreateDTO) -> NotificationDTO:
        """
        Create a new notification.

        Parameters
        ----------
        dto : NotificationCreateDTO
            Data for creating the notification.

        Returns
        -------
        NotificationDTO
            Newly created notification.
        """
        notif = await self.repo.create(
            user_id=dto.user_id, message=dto.message, read=False, type=dto.type
        )
        return db_to_dto(notif)

    async def delete(self, id: int) -> bool:
        """
        Delete a notification by its ID.

        Returns
        -------
        bool
            True if deleted, False otherwise.
        """
        return await self.repo.delete(id)

    async def get_by_user(self, user_id: int) -> list[NotificationDTO]:
        """
        Retrieve all notifications for a specific user.

        Parameters
        ----------
        user_id : int
            ID of the user.

        Returns
        -------
        list[NotificationDTO]
            User's notifications.
        """
        notifs = await self.repo.get_by_user(user_id)
        return [db_to_dto(n) for n in notifs]

    async def dismiss(self, id: int, user_id: int) -> bool:
        """
        Mark a notification as read (dismiss) for a user.

        Parameters
        ----------
        id : int
            Notification ID.
        user_id : int
            ID of the user.

        Returns
        -------
        bool
            True if dismissed, False otherwise.

        Raises
        ------
        HTTPException
            If the notification does not exist or does not belong to the user.
        """
        notif = await self.repo.get_by_id(id)
        if notif is None or notif.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found"
            )
        return await self.repo.mark_as_read(id)

    async def get_by_user_and_type(
        self, user_id: int, type_: str
    ) -> list[NotificationDTO]:
        """
        Retrieve notifications of a specific type for a user.

        Parameters
        ----------
        user_id : int
            ID of the user.
        type_ : str
            Notification type.

        Returns
        -------
        list[NotificationDTO]
            User's notifications of the given type.
        """
        notifs = await self.repo.get_by_user_and_type(user_id, type_)
        return [db_to_dto(n) for n in notifs]
