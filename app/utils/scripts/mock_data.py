import asyncio
import logging
import random
import uuid
from datetime import datetime

from app.models.enums import DeviceType, NotificationType
from app.models.db import UserDb, GardenDb, DeviceDb, ReadingDb, NotificationDb
from app.core.db_context import async_session_maker

# Logger setup
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def mock():
    async with async_session_maker() as session:
        # Clean all data
        await session.execute(NotificationDb.__table__.delete())
        await session.execute(ReadingDb.__table__.delete())
        await session.execute(DeviceDb.__table__.delete())
        await session.execute(GardenDb.__table__.delete())
        await session.execute(UserDb.__table__.delete())
        await session.commit()
        logger.info("Database cleared.")

        for i in range(3):
            user = UserDb(
                email=f"user{i}@example.com",
                google_sub=None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(user)
            await session.flush()  # get user.id

            logger.info(f"Created user {user.email}")

            for g in range(2):
                garden = GardenDb(
                    user_id=user.id,
                    name=f"{user.email}_garden_{g}",
                    send_notifications=False,
                    enable_automation=True,
                    use_fahrenheit=False,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(garden)
                await session.flush()  # get garden.id

                logger.info(f"  Created garden {garden.name}")

                for device_type in DeviceType:
                    device = DeviceDb(
                        garden_id=garden.id,
                        mac=str(uuid.uuid4()),
                        type=device_type,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    session.add(device)
                    await session.flush()  # get device.id

                    logger.info(f"    Created device {device.type.value} for garden {garden.name}")

                    for _ in range(3):
                        reading = ReadingDb(
                            device_id=device.id,
                            value=f"{random.uniform(10, 100):.2f}",
                            timestamp=datetime.utcnow()
                        )
                        session.add(reading)

                logger.info(f"    Added readings for all devices in {garden.name}")

            for notif_type in NotificationType:
                notif = NotificationDb(
                    user_id=user.id,
                    message=f"Test {notif_type.value} notification",
                    type=notif_type,
                    read=False,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(notif)

            logger.info(f"  Created notifications for {user.email}")

        await session.commit()
        logger.info("Mock data generation complete.")


if __name__ == "__main__":
    asyncio.run(mock())
