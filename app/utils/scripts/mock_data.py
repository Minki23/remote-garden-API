import asyncio
import logging
import random
import uuid
from datetime import datetime, timedelta

from app.models.enums import DeviceType, NotificationType
from app.models.db import (
    UserDb, GardenDb, DeviceDb, ReadingDb,
    NotificationDb, EspDeviceDb, UserDeviceDb
)
from app.core.db_context import async_session_maker

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def generate_realistic_reading_value(device_type: DeviceType) -> str:
    """Generate realistic sensor values based on device type."""
    value_ranges = {
        DeviceType.LIGHT_SENSOR: lambda: str(random.randint(50, 1000)),
        DeviceType.AIR_HUMIDITY_SENSOR: lambda: f"{random.uniform(35.0, 85.0):.1f}",
        DeviceType.SOIL_MOISTURE_SENSOR: lambda: f"{random.uniform(15.0, 75.0):.1f}",
        DeviceType.AIR_TEMPERATURE_SENSOR: lambda: f"{random.uniform(18.0, 32.0):.1f}",
        DeviceType.SIGNAL_STRENGHT: lambda: str(random.randint(-80, -25)),
        DeviceType.BATTERY: lambda: f"{random.uniform(25.0, 100.0):.1f}",
        DeviceType.WATERER: lambda: str(random.choice([0, 1])),
        DeviceType.ATOMIZER: lambda: str(random.choice([0, 1])),
        DeviceType.FANNER: lambda: str(random.choice([0, 1])),
        DeviceType.HEATER: lambda: str(random.choice([0, 1]))
    }

    return value_ranges.get(device_type, lambda: f"{random.uniform(0, 100):.2f}")()


def get_notification_messages():
    """Return predefined notification messages for each type."""
    return {
        NotificationType.alert: [
            "Critical: Soil moisture below 20% in Garden Alpha",
            "Warning: Temperature exceeds 35°C - plants at risk",
            "Alert: ESP device battery critically low (8%)",
            "Danger: Water tank empty - automatic watering disabled",
            "Critical: No data from ESP device for 2 hours"
        ],
        NotificationType.reminder: [
            "Weekly reminder: Check and clean sensors",
            "Monthly task: Calibrate soil moisture sensors",
            "Reminder: Refill water reservoir",
            "Don't forget: Inspect plant health today",
            "Scheduled: Update ESP firmware available"
        ],
        NotificationType.system: [
            "System: Automatic watering cycle completed",
            "Info: New ESP device successfully paired",
            "Update: All sensors synchronized",
            "System: Backup completed successfully",
            "Info: Network connectivity restored"
        ]
    }


async def clear_all_data(session):
    """Clear all existing data from database in correct order."""
    tables_to_clear = [
        ReadingDb.__table__,
        DeviceDb.__table__,
        EspDeviceDb.__table__,
        NotificationDb.__table__,
        UserDeviceDb.__table__,
        GardenDb.__table__,
        UserDb.__table__
    ]

    for table in tables_to_clear:
        await session.execute(table.delete())

    await session.commit()
    logger.info("✓ Database cleared successfully")


async def create_users_and_devices(session, num_users=4):
    """Create users with their mobile devices."""
    users = []
    platforms = ["android", "ios"]

    for i in range(num_users):
        # Create user
        user = UserDb(
            email=f"gardener{i+1}@greenhouse.com",
            google_sub=f"google_sub_{uuid.uuid4().hex[:16]}",
            auth=f"auth_{uuid.uuid4().hex}",
            admin=(i == 0),  # First user is admin
        )
        session.add(user)
        await session.flush()
        users.append(user)

        logger.info(
            f"✓ Created user: {user.email} {'(ADMIN)' if user.admin else ''}")

        # Create mobile devices for user
        num_devices = random.randint(1, 3)
        for d in range(num_devices):
            user_device = UserDeviceDb(
                user_id=user.id,
                fcm_token=f"fcm_{uuid.uuid4().hex}",
                platform=platforms[d % len(platforms)],
                last_seen=datetime.utcnow() - timedelta(hours=random.randint(0, 48))
            )
            session.add(user_device)

        logger.info(f"  → Added {num_devices} mobile devices")

    return users


async def create_gardens_with_esp_devices(session, users):
    """Create gardens and their ESP devices."""
    all_esp_devices = []

    for user in users:
        num_gardens = random.randint(1, 3)

        for g in range(num_gardens):
            # Create garden
            garden = GardenDb(
                user_id=user.id,
                name=f"{user.email.split('@')[0]}_garden_{g+1}",
                send_notifications=random.choice([True, False]),
                enable_automation=random.choice([True, False]),
                use_fahrenheit=random.choice([True, False])
            )
            session.add(garden)
            await session.flush()

            logger.info(f"✓ Created garden: {garden.name}")
            logger.info(
                f"  → Notifications: {garden.send_notifications}, Automation: {garden.enable_automation}")

            # Create ESP devices for garden
            num_esp = random.randint(1, 2)
            for e in range(num_esp):
                mac_address = ":".join(
                    [f"{random.randint(0, 255):02X}" for _ in range(6)])

                esp_device = EspDeviceDb(
                    mac=mac_address,
                    secret=f"secret_{uuid.uuid4().hex[:16]}",
                    client_key=f"key_{uuid.uuid4().hex}" if random.choice([
                        True, False]) else None,
                    client_crt=f"cert_{uuid.uuid4().hex}" if random.choice([
                        True, False]) else None,
                    garden_id=garden.id,
                    user_id=user.id,
                    status=random.choice([True, True, False])  # 66% online
                )
                session.add(esp_device)
                await session.flush()
                all_esp_devices.append(esp_device)

                logger.info(
                    f"  → ESP Device: {esp_device.mac} (Status: {'Online' if esp_device.status else 'Offline'})")

    return all_esp_devices


async def create_devices_and_readings(session, esp_devices):
    """Create sensor/actuator devices and their readings."""

    # Define which devices each ESP should have
    essential_sensors = [
        DeviceType.AIR_TEMPERATURE_SENSOR,
        DeviceType.AIR_HUMIDITY_SENSOR,
        DeviceType.SOIL_MOISTURE_SENSOR,
        DeviceType.LIGHT_SENSOR,
        DeviceType.BATTERY,
        DeviceType.SIGNAL_STRENGHT
    ]

    optional_actuators = [
        DeviceType.WATERER,
        DeviceType.ATOMIZER,
        DeviceType.FANNER,
        DeviceType.HEATER
    ]

    for esp in esp_devices:
        # Add all essential sensors
        device_types_to_add = essential_sensors.copy()

        # Add random actuators
        num_actuators = random.randint(1, len(optional_actuators))
        selected_actuators = random.sample(optional_actuators, num_actuators)
        device_types_to_add.extend(selected_actuators)

        logger.info(
            f"  ESP {esp.mac}: Adding {len(device_types_to_add)} devices")

        for device_type in device_types_to_add:
            # Create device
            device = DeviceDb(
                esp_id=esp.id,
                type=device_type,
                enabled=random.choice([True, False, None])
            )
            session.add(device)
            await session.flush()

            # Create readings for the device
            num_readings = random.randint(3, 8)
            for r in range(num_readings):
                reading_time = datetime.utcnow() - timedelta(
                    hours=random.randint(0, 72),
                    minutes=random.randint(0, 59)
                )

                reading = ReadingDb(
                    device_id=device.id,
                    value=generate_realistic_reading_value(device_type),
                    timestamp=reading_time
                )
                session.add(reading)

            logger.info(f"    → {device_type.value}: {num_readings} readings")


async def create_notifications(session, users):
    """Create notifications for users."""
    notification_messages = get_notification_messages()

    for user in users:
        num_notifications = random.randint(2, 6)

        for _ in range(num_notifications):
            notif_type = random.choice(list(NotificationType))
            message = random.choice(notification_messages[notif_type])

            notification = NotificationDb(
                user_id=user.id,
                message=message,
                type=notif_type,
                read=random.choice([True, False]),
                created_at=datetime.utcnow() - timedelta(
                    hours=random.randint(0, 168)  # Last week
                )
            )
            session.add(notification)

        logger.info(
            f"✓ Created {num_notifications} notifications for {user.email}")


async def print_summary(session):
    """Print summary of created data."""
    from sqlalchemy import func, select

    # Count records
    user_count = (await session.execute(select(func.count(UserDb.id)))).scalar()
    garden_count = (await session.execute(select(func.count(GardenDb.id)))).scalar()
    esp_count = (await session.execute(select(func.count(EspDeviceDb.id)))).scalar()
    device_count = (await session.execute(select(func.count(DeviceDb.id)))).scalar()
    reading_count = (await session.execute(select(func.count(ReadingDb.id)))).scalar()
    notification_count = (await session.execute(select(func.count(NotificationDb.id)))).scalar()
    user_device_count = (await session.execute(select(func.count(UserDeviceDb.id)))).scalar()

    print("\n" + "="*50)
    print("📊 MOCK DATA GENERATION SUMMARY")
    print("="*50)
    print(f"👥 Users: {user_count}")
    print(f"📱 User Devices: {user_device_count}")
    print(f"🌱 Gardens: {garden_count}")
    print(f"🔧 ESP Devices: {esp_count}")
    print(f"📡 Sensor/Actuator Devices: {device_count}")
    print(f"📈 Sensor Readings: {reading_count}")
    print(f"🔔 Notifications: {notification_count}")
    print("="*50)


async def generate_mock_data():
    """Main function to generate all mock data."""
    logger.info("🚀 Starting mock data generation...")

    async with async_session_maker() as session:
        try:
            # Clear existing data
            await clear_all_data(session)

            # Create users and their devices
            users = await create_users_and_devices(session)

            # Create gardens with ESP devices
            esp_devices = await create_gardens_with_esp_devices(session, users)

            # Create sensor devices and readings
            await create_devices_and_readings(session, esp_devices)

            # Create notifications
            await create_notifications(session, users)

            # Commit all changes
            await session.commit()
            logger.info("💾 All data committed to database")

            # Print summary
            await print_summary(session)

            logger.info("✅ Mock data generation completed successfully!")

        except Exception as e:
            logger.error(f"❌ Error during mock data generation: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(generate_mock_data())
