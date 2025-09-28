import logging
from typing import List

from clients.csr_client import CsrClient
from core.mqtt.mqtt_publisher import MqttTopicPublisher
from exceptions.scheme import AppException
from mappers.esp_devices import db_esp_to_dto
from common_db.db import EspDeviceDb
from models.dtos.esp_device import EspDeviceDTO
from repos.esp_devices import EspDeviceRepository
from repos.users import UserRepository

logger = logging.getLogger(__name__)


class EspDeviceService:
    """
    Service for managing ESP devices, including registration, assignment,
    MQTT control, and certificate handling.
    """

    def __init__(self, repo: EspDeviceRepository, user_repo: UserRepository):
        """
        Initialize the service.
        """
        self.repo = repo
        self.user_repo = user_repo
        self.csr_client = CsrClient()

    async def get_own(self, user_id: int) -> List[EspDeviceDTO]:
        """
        Retrieve all ESP devices owned by a user.

        Parameters
        ----------
        user_id : int
            ID of the user.

        Returns
        -------
        List[EspDeviceDTO]
            List of ESP devices mapped to DTOs.
        """
        devices = await self.repo.get_by_user_id(user_id)
        return [db_esp_to_dto(d) for d in devices]

    async def assign_to_garden(self, esp_id: int, garden_id: int) -> None:
        """
        Assign an ESP device to a garden.
        """
        await self.repo.update(esp_id, garden_id=garden_id)

    async def unassign_from_garden(self, esp_id: int, user_id: int) -> None:
        """
        Remove the garden assignment from an ESP device,
        ensuring the device belongs to the requesting user.
        """
        esp = await self.repo.get_by_id(esp_id)
        if not esp:
            raise AppException(message="ESP device not found", status_code=404)
        if esp.user_id != user_id:
            raise AppException(message="Not authorized", status_code=403)

        await self.repo.update(esp_id, garden_id=None)

    async def register_new_device(self, mac: str, secret: str) -> EspDeviceDb:
        """
        Register a new ESP device with MAC and secret.
        """
        logger.info(f"Try to register new device: {mac}")
        existing = await self.repo.get_by_mac(mac)
        if existing:
            logger.warning("Device exists")
            raise AppException("Device already exists")

        return await self.repo.create(mac=mac, secret=secret)

    async def _validate_device(self, esp_id: int, user_id: int) -> EspDeviceDb:
        """
        Ensure that an ESP device exists, belongs to the user, and has a MAC.
        """
        esp = await self.repo.get_by_id(esp_id)
        if not esp or esp.user_id != user_id:
            raise AppException(
                "ESP device not found or not owned by user", 404)

        if not esp.mac:
            raise AppException("ESP device MAC address not set", 400)

        return esp

    async def reset_device(self, esp_id: int, user_id: int) -> None:
        """
        Reset the ESP device, removing all assignments and credentials.
        Sends a reset command via MQTT.
        """
        esp = await self._validate_device(esp_id, user_id)

        await self.repo.update(
            esp_id,
            garden_id=None,
            user_id=None,
            client_key=None,
            client_crt=None,
        )

        publisher = MqttTopicPublisher()
        await publisher.publish(topic=f"{esp.mac}/reset", payload={})

    async def stop_device(self, esp_id: int, user_id: int) -> None:
        """
        Stop an ESP device via MQTT.
        """
        esp = await self._validate_device(esp_id, user_id)

        publisher = MqttTopicPublisher()
        await publisher.publish(topic=f"{esp.mac}/stop", payload={})

    async def resume_device(self, esp_id: int, user_id: int) -> None:
        """
        Resume a stopped ESP device via MQTT.
        """
        esp = await self._validate_device(esp_id, user_id)

        publisher = MqttTopicPublisher()
        await publisher.publish(topic=f"{esp.mac}/resume", payload={})

    async def process_csr_and_issue_cert(
        self, device_id: str, device_secret: str, user_key: str, csr_pem: str
    ) -> str:
        """
        Process a CSR from a device, validate it, and issue a certificate.

        Parameters
        ----------
        device_id : str
            ESP device ID (MAC).
        device_secret : str
            Device secret for authentication.
        user_key : str
            User key for ownership validation.
        csr_pem : str
            CSR PEM string submitted by the device.

        Returns
        -------
        str
            Signed certificate PEM.
        """
        device = await self.repo.get_by_client(device_id, device_secret)
        if not device:
            raise AppException("Invalid device credentials")

        user = await self.user_repo.get_by_user_key(user_key)
        if not user:
            raise AppException("Invalid user key")

        cert_pem = await self.csr_client.sign_csr(csr_pem)
        await self.repo.update(device.id, client_crt=cert_pem, user_id=user.id)
        return cert_pem
