from typing import Optional
from models.dtos.notifications import NotificationDTO, NotificationCreateDTO
from services.notifications import NotificationService
from services.user_devices import UserDeviceService
from controllers.push.firebase_wrapper import FirebaseWrapper

from repos.notifications import NotificationRepository
from repos.user_device import UserDeviceRepository
from core.db_context import async_session_maker


class PushNotificationController:
    def __init__(
        self,
        notification_service: NotificationService,
        user_device_service: UserDeviceService,
        push_service: FirebaseWrapper,
    ):
        self.notification_service = notification_service
        self.user_device_service = user_device_service
        self.push_service = push_service

    async def create_push_notification(
        self,
        dto: NotificationCreateDTO,
        send_push: bool = True,
    ) -> NotificationDTO:
        notif = await self.notification_service.create(dto)

        if send_push:
            tokens = await self.user_device_service.get_user_tokens(dto.user_id)
            if tokens:
                await self.push_service.send_to_tokens(
                    tokens,
                    title="Nowe powiadomienie",
                    body=dto.message,
                    data={"type": dto.type},
                )

        return notif

    @staticmethod
    async def send(dto: NotificationCreateDTO, send_push: bool = True) -> NotificationDTO:
        async with async_session_maker() as session:
            notif_service = NotificationService(
                NotificationRepository(session))
            device_service = UserDeviceService(UserDeviceRepository(session))
            push_service = FirebaseWrapper()

            controller = PushNotificationController(
                notification_service=notif_service,
                user_device_service=device_service,
                push_service=push_service,
            )
            return await controller.create_push_notification(dto, send_push=send_push)
