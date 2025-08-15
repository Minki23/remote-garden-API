from app.models.db import EspDeviceDb
from app.repos.esp_devices import EspDeviceRepository
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from datetime import datetime, timedelta

# TODO podczas tworzenia esp automatycznie sie tworza devices do niego
# esp juz siedza w bazie i klikajac paruj wysyla sie do esp a esp wysyla do rest sygnal register i ten register wlasnie waliduje itd
# a do bazy devices tez sa defaultowo - tak zrobic aby nie byly skojarzone z garden
# zrobic tak ze podlaczam po uart esp i puszczam skrypt i on automatycznie wrzuca na esp te 2 klucze co default i tworzy wszystko w bazie co konieczne (devices i esp)
# a po register dorzucaja sie dwa kolejne klucze tzn wtedy ze jest zautoryzowany
# a garden totalnie niezalezne
# topic na mqtt zrobic jako po garden i zrobic tak ze jak ktos odlaczy esp od garden to automatycznie esp nie subkrybuje juz tych topicow (albo jak przypisanie do nowego garden)
#    auto [clientKey, clientCert, caCert, deviceId] =
#        DeviceProvisioner::loadTlsCredentials();
# to waliduje przy odbiorze danych z brokera


class EspDeviceService:
    def __init__(self, repo: EspDeviceRepository):
        self.repo = repo

    async def register_new_device(self, mac: str, secret: str) -> EspDeviceDb:
        existing = await self.repo.get_by_mac(mac)
        if existing:
            raise ValueError("Device already exists")

        return await self.repo.create(
            mac=mac,
            secret=secret,
            # client_key=None,
            # client_crt=None,
            # garden_id=None,
            # created_at=datetime.utcnow(),
            # updated_at=datetime.utcnow(),
        )

    async def process_csr_and_issue_cert(
        self, device_id: str, device_secret: str, csr_pem: str
    ) -> str:
        device = await self.repo.get_by_client(device_id, device_secret)
        if not device:
            raise ValueError("Invalid device credentials")

        csr = x509.load_pem_x509_csr(csr_pem.encode(), backend=default_backend())
        if not csr.is_signature_valid:
            raise ValueError("CSR signature invalid")

        cert = self._sign_certificate(csr)
        await self.repo.save_certificate(device_id, cert)
        return cert.public_bytes(serialization.Encoding.PEM).decode()

    def _sign_certificate(
        self, csr: x509.CertificateSigningRequest
    ) -> x509.Certificate:
        with open("ca/ca.key", "rb") as f:
            ca_private_key = serialization.load_pem_private_key(f.read(), password=None)

        with open("ca/ca.crt", "rb") as f:
            ca_cert = x509.load_pem_x509_certificate(f.read(), default_backend())

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
