import logging
from controllers.mqtt_handlers.base_device_handler import BaseDeviceHandler
from core.db_context import async_session_maker
from models.dtos.notifications import NotificationCreateDTO
from repos.notifications import NotificationRepository
from services.notifications import NotificationService
from repos.devices import DeviceRepository
from common_db.enums import DeviceType, NotificationType

logger = logging.getLogger(__name__)

ACTUATOR_STR_TO_DEVICE_TYPE = {
    "water": DeviceType.WATERER,
    "fan": DeviceType.FANNER,
    "atomize": DeviceType.ATOMIZER,
    "heating_mat": DeviceType.HEATER,
}


class ActuatorConfirmHandler(BaseDeviceHandler):
    """
    MQTT handler responsible for processing actuator confirmation messages.
    Subscribed to the topic pattern ``{mac}/device/confirm``.

    This handler updates device states in the database and, if possible,
    triggers user notifications about actuator state changes.
    """

    def __init__(self):
        """
        Initialize the handler with the appropriate MQTT topic template.
        """
        super().__init__("{mac}/device/confirm")

    async def __call__(self, topic: str, payload: dict):
        """
        Handle an incoming actuator confirmation MQTT message.

        Parameters
        ----------
        topic : str
            The MQTT topic that carried the message.
        payload : dict
            The parsed JSON payload with fields like:
              - ``device``: string name of actuator (e.g. "water").
              - ``action``: expected to be "on" or "off".
              - ``status``: confirmation status of the action.

        Returns
        -------
        """
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

                if user:
                    not_service = NotificationService(
                        NotificationRepository(session))
                    status = "enabled" if new_enabled else "disabled"
                    await not_service.create(
                        NotificationCreateDTO(
                            user_id=user.id,
                            message=f"Device {device_type} is {status}",
                            type=NotificationType.alert,
                        )
                    )
                else:
                    logger.warning(
                        "Cannot send notification because owner of esp is not specified"
                    )
