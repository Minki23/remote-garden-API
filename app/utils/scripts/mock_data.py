import asyncio
import random
from datetime import datetime

from app.models.enums import DeviceType, ScheduleActionType, NotificationType
from app.models.dtos.users import UserCreateDTO
from app.models.dtos.gardens import GardenCreateDTO
from app.models.dtos.readings import ReadingCreateDTO
from app.models.dtos.notifications import NotificationCreateDTO

from app.core.db_context import async_session_maker
from app.services.users import UserService
from app.services.gardens import GardenService
from app.services.devices import DeviceService
from app.services.readings import ReadingService
from app.services.notifications import NotificationService
from app.services.schedules import ScheduleService

from app.repos.users import UserRepository
from app.repos.gardens import GardenRepository
from app.repos.devices import DeviceRepository
from app.repos.readings import ReadingRepository
from app.repos.notifications import NotificationRepository
from app.repos.schedules import ScheduleRepository

from app.models.db import UserDb, GardenDb, DeviceDb, ReadingDb, NotificationDb


async def mock():
    async with async_session_maker() as db:
        await db.execute(NotificationDb.__table__.delete())
        await db.execute(ReadingDb.__table__.delete())
        await db.execute(DeviceDb.__table__.delete())
        await db.execute(GardenDb.__table__.delete())
        await db.execute(UserDb.__table__.delete())
        await db.commit()

        user_service = UserService(UserRepository(db))
        device_service = DeviceService(DeviceRepository(db))
        garden_service = GardenService(GardenRepository(db), device_service)
        reading_service = ReadingService(ReadingRepository(db))
        notif_service = NotificationService(NotificationRepository(db))
        schedule_service = ScheduleService(ScheduleRepository())

        for i in range(10):
            email = f"user{i}@example.com"
            try:
                user = await user_service.create_user(UserCreateDTO(email=email))
            except Exception:
                continue

            for g in range(2):
                garden = await garden_service.create_garden(
                    GardenCreateDTO(name=f"{email}_garden_{g}"), user.id
                )

                devices = await device_service.get_all_for_garden(garden.id)

                for device in devices:
                    for _ in range(10):
                        await reading_service.create(
                            ReadingCreateDTO(
                                device_id=device.id, value=f"{random.uniform(10, 100):.2f}"
                            )
                        )

                # 2 schedules per garden
                for action in [ScheduleActionType.START_WATERING, ScheduleActionType.OPEN_ROOF]:
                    minute = random.randint(0, 59)
                    hour = random.randint(0, 23)
                    cron = f"{minute} {hour} * * *"
                    schedule_service.create(garden.id, cron, action)

            # 3 notifications per user
            for notif_type in NotificationType:
                await notif_service.create(
                    NotificationCreateDTO(
                        user_id=user.id, message=f"Mock {notif_type.value} message", type=notif_type
                    )
                )


if __name__ == "__main__":
    asyncio.run(mock())
