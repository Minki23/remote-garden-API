import logging
from typing import List
from app.core.mqtt.mqtt_publisher import MqttTopicPublisher
from app.exceptions.scheme import AppException
from app.mappers.esp_devices import db_esp_to_dto
from app.models.db import EspDeviceDb
from app.models.dtos.esp_device import EspDeviceDTO
from app.repos.esp_devices import EspDeviceRepository
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from datetime import datetime, timedelta

# TODO podczas tworzenia esp automatycznie sie tworza devices do niego
# esp juz siedza w bazie i klikajac paruj wysyla sie do esp a esp wysyla do rest sygnal register i ten register wlasnie waliduje itd
# a do bazy devices tez sa defaultowo - tak zrobic aby nie byly skojarzone z garden
# zrobic tak ze podlaczam po uart esp i puszczam skrypt i on automatycznie wrzuca na esp te 2 klucze co default i
# tworzy wszystko w bazie co konieczne (devices i esp)
# a po register dorzucaja sie dwa kolejne klucze tzn wtedy ze jest zautoryzowany
# a garden totalnie niezalezne
# topic na mqtt zrobic jako po garden i zrobic tak ze jak ktos odlaczy esp od garden to automatycznie esp nie subkrybuje juz tych topicow (albo jak przypisanie do nowego garden)
#    auto [clientKey, clientCert, caCert, deviceId] =
#        DeviceProvisioner::loadTlsCredentials();
# to waliduje przy odbiorze danych z brokera

logger = logging.getLogger(__name__)


class EspDeviceService:
    def __init__(self, repo: EspDeviceRepository):
        self.repo = repo

    async def get_own(self, user_id: int) -> List[EspDeviceDTO]:
        devices = await self.repo.get_by_user_id(user_id)
        return [db_esp_to_dto(d) for d in devices]

    async def assign_to_garden(self, esp_id: int, garden_id: int, user_id: int) -> None:
        esp = await self.repo.get_by_id(esp_id)
        if not esp or esp.user_id != user_id:
            raise AppException(
                message="ESP device not found or not owned by user", status_code=404)

        await self.repo.update(esp_id, garden_id=garden_id)

    async def unassign_from_garden(self, esp_id: int, user_id: int) -> None:
        esp = await self.repo.get_by_id(esp_id)
        if not esp:
            raise AppException(message="ESP device not found", status_code=404)
        if esp.user_id != user_id:
            raise AppException(message="Not authorized", status_code=403)

        await self.repo.update(esp_id, garden_id=None)

    async def register_new_device(self, mac: str, secret: str) -> EspDeviceDb:
        logger.info(f"Try to register new device: {mac}")
        existing = await self.repo.get_by_mac(mac)
        if existing:
            logger.warning("Device exists")
            raise AppException("Device already exists")

        return await self.repo.create(
            mac=mac,
            secret=secret,
        )

    async def reset_device(self, esp_id: int, user_id: int) -> None:
        esp = await self.repo.get_by_id(esp_id)
        if not esp or esp.user_id != user_id:
            raise AppException(
                "ESP device not found or not owned by user", 404)

        if not esp.mac:
            raise AppException("ESP device MAC address not set", 400)

        await self.repo.update(
            esp_id,
            garden_id=None,
            user_id=None,
            client_key=None,
            client_crt=None
        )

        publisher = MqttTopicPublisher()
        await publisher.publish(
            topic=f"/{esp.mac}/reset",
            payload={}
        )

    async def process_csr_and_issue_cert(
        self, device_id: str, device_secret: str, csr_pem: str
    ) -> str:
        device = await self.repo.get_by_client(device_id, device_secret)
        if not device:
            raise AppException("Invalid device credentials")

        csr = x509.load_pem_x509_csr(
            csr_pem.encode(), backend=default_backend())
        if not csr.is_signature_valid:
            raise AppException("CSR signature invalid")

        cert = self._sign_certificate(csr)

        await self.repo.update(
            device.id,
            client_crt=cert.public_bytes(serialization.Encoding.PEM).decode()
        )

        return cert.public_bytes(serialization.Encoding.PEM).decode()

    def _sign_certificate(
        self, csr: x509.CertificateSigningRequest
    ) -> x509.Certificate:
        with open("ca/ca.key", "rb") as f:
            ca_private_key = serialization.load_pem_private_key(
                f.read(), password=None)

        with open("ca/ca.crt", "rb") as f:
            ca_cert = x509.load_pem_x509_certificate(
                f.read(), default_backend())

        subject = csr.subject
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(ca_cert.subject)
            .public_key(csr.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.utcnow())
            .not_valid_after(datetime.utcnow() + timedelta(days=365))
            .add_extension(
                x509.BasicConstraints(ca=False, path_length=None), critical=True
            )
            .sign(ca_private_key, hashes.SHA256())
        )
        return cert
