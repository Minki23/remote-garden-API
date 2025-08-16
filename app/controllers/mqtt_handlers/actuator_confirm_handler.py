import logging
from app.controllers.mqtt_handlers.base_device_handler import BaseDeviceHandler
from app.core.mqtt.base_mqtt_callback_handler import BaseMqttCallbackHandler
from app.core.db_context import async_session_maker
from app.core.websocket.websocket_manager import websocket_manager
from app.models.dtos.notifications import NotificationCreateDTO
from app.repos.notifications import NotificationRepository
from app.services.notifications import NotificationService
from app.services.readings import ReadingService
from app.repos.readings import ReadingRepository
from app.repos.devices import DeviceRepository
from app.repos.users import UserRepository
from app.models.enums import DeviceType, NotificationType
from app.models.dtos.readings import ReadingCreateDTO

logger = logging.getLogger(__name__)

ACTUATOR_STR_TO_DEVICE_TYPE = {
    "water": DeviceType.WATERER,
    "fan": DeviceType.FANNER,
    "atomize": DeviceType.ATOMIZER,
    "heating_mat": DeviceType.HEATER,
}


class ActuatorConfirmHandler(BaseDeviceHandler):
    def __init__(self):
        super().__init__("{mac}/device/confirm")

    async def __call__(self, topic: str, payload: dict):
        logger.info(f"[ACTUATOR_CONFIRM] topic={topic}, payload={payload}")

        device_str = payload.get("device")
        if device_str not in ACTUATOR_STR_TO_DEVICE_TYPE:
            logger.warning(f"Unknown actuator type '{device_str}' in payload.")
            return
        device_type = ACTUATOR_STR_TO_DEVICE_TYPE[device_str]

        action = payload.get("action")
        status = payload.get("status")
        if action not in ("on", "off") or status is None:
            logger.warning(f"Invalid actuator confirm payload: {payload}")
            return

        try:
            mac = self.extract_from_topic(topic, "mac")
        except (ValueError, TypeError):
            logger.warning(f"Could not extract valid mac from topic: {topic}")
            return

        device, user = await self.process_device_event(
            topic,
            mac,
            device_type,
            payload,
            websocket_event="actuator_confirm",
            extra_fields={"action": action, "status": status},
        )

        if device and status:
            async with async_session_maker() as session:
                new_enabled = True if action == "on" else False

                device_repo = DeviceRepository(session)
                await device_repo.update(device.id, enabled=new_enabled)

                not_service = NotificationService(
                    NotificationRepository(session))
                status = "enabled" if new_enabled else "disabled"
                not_service.create(NotificationCreateDTO(
                    user_id=user.id, message=f"Device {device_type} is {status}", type=NotificationType.alert))
