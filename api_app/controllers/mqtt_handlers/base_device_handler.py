import logging
from core.mqtt.base_mqtt_callback_handler import BaseMqttCallbackHandler
from core.db_context import async_session_maker
from repos.devices import DeviceRepository
from repos.agents import AgentRepository
from core.websocket.websocket_manager import websocket_manager

logger = logging.getLogger(__name__)


class BaseDeviceHandler(BaseMqttCallbackHandler):
    """
    Base class for handling MQTT device-related events.
    Extends :class:`BaseMqttCallbackHandler` with reusable logic for
    updating device state, resolving garden ownership, and
    propagating messages via WebSocket to both users and agents.
    """

    def __init__(self, topic_template: str):
        """
        Initialize the handler with the given topic template.

        Parameters
        ----------
        topic_template : str
            MQTT topic pattern used by this handler (e.g. ``{mac}/device/confirm``).
        """
        super().__init__(topic_template)

    async def process_device_event(
        self,
        topic: str,
        mac: str,
        device_type,
        payload: dict,
        websocket_event: str,
        extra_fields: dict,
    ):
        """
        Process a device event by resolving the device and its owner,
        sending notifications over WebSocket, and optionally notifying
        the agent assigned to the garden.

        Parameters
        ----------
        topic : str
            The MQTT topic that triggered this event.
        mac : str
            MAC address of the ESP device from the topic.
        device_type : DeviceType
            The type of the device (e.g. waterer, fan).
        payload : dict
            Raw JSON payload of the MQTT message.
        websocket_event : str
            Event name to broadcast via WebSocket (e.g. "actuator_confirm").
        extra_fields : dict
            Additional fields to include in the WebSocket event.

        Returns
        -------
        tuple
            A tuple ``(device, user)`` where:
              - ``device`` is the resolved device entity or ``None``.
              - ``user`` is the owner of the ESP device or ``None``.
        """
        async with async_session_maker() as session:
            device_repo = DeviceRepository(session)
            device = await device_repo.get_device_by_type_for_esp_mac(mac, device_type)
            if not device:
                logger.warning(
                    f"No {device_type.name} device found for esp with mac {mac}"
                )
                return None, None

            esp = device.esp
            garden_id = esp.garden_id
            user = esp.user
            if not user:
                logger.warning(f"User not found for esp with mac {mac}")
                return device, None

            event_data = {
                "event": websocket_event,
                "device_type": device_type.value,
                "esp_mac": mac,
                "garden_id": garden_id,
                "device_id": device.id,
                **extra_fields,
            }
            await websocket_manager.send_to_user(user.id, event_data)

            logger.info(f"WebSocket {websocket_event} sent to user {user.id}")

            agent_repo = AgentRepository(session)
            agent = await agent_repo.get_by_garden(garden_id)

            if agent:
                await websocket_manager.send_to_agent(agent.id, event_data)

            return device, user
