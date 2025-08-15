import os
import subprocess
import serial.tools.list_ports
import binascii
import logging
import argparse
import shutil
import requests

# ---- DATABASE-LIKE CONST ----
ESPTOOL = "esptool.py"
SPIFFS_OFFSET = "0x220000"
SPIFFS_SIZE = 0x60000
DATA_DIR = "spiffs_data"
BIN_FILE = "spiffs.bin"
DEFAULT_CA_PATH = "/workspaces/remote-garden-API/app/ca/ca.crt"
DEFAULT_API_URL = "http://localhost:8000/api/admin/esp/create"

# ---- LOGGING ----
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def find_esp_port():
    ports = serial.tools.list_ports.comports()
    for p in ports:
        if "USB" in p.description or "UART" in p.description:
            return p.device
    return None


def read_mac(port):
    try:
        result = subprocess.check_output(
            [ESPTOOL, "--chip", "esp32", "--port", port, "read_mac"], text=True
        )
        for line in result.splitlines():
            if "MAC:" in line:
                mac = line.strip().split("MAC:")[1].strip()
                return mac.replace(":", "").lower()
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to read MAC address: {e}")
    return None


def generate_secret():
    return binascii.hexlify(os.urandom(64)).decode()  # 512-bit hex string


def prepare_files(mac, secret, ca_path):
    os.makedirs(DATA_DIR, exist_ok=True)

    with open(os.path.join(DATA_DIR, "device_id.txt"), "w") as f:
        f.write(mac)
    with open(os.path.join(DATA_DIR, "device_secret.txt"), "w") as f:
        f.write(secret)

    if not os.path.isfile(ca_path):
        logger.error(f"CA certificate not found at: {ca_path}")
        raise FileNotFoundError(f"No such file: {ca_path}")

    shutil.copy(ca_path, os.path.join(DATA_DIR, "ca.crt"))
    logger.info("Copied CA certificate to SPIFFS data directory.")


def create_spiffs_image():
    cmd = f"mkspiffs -c {DATA_DIR} -b 4096 -p 256 -s {SPIFFS_SIZE} {BIN_FILE}"
    subprocess.check_call(cmd, shell=True)


def flash_spiffs(port):
    cmd = f"{ESPTOOL} --chip esp32 --port {port} --baud 460800 write_flash {SPIFFS_OFFSET} {BIN_FILE}"
    subprocess.check_call(cmd, shell=True)


def register_device_remotely(mac: str, secret: str, api_url: str, token: str):
    payload = {"mac": mac, "secret": secret}
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.post(
            api_url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        logger.info("ESP device registered via API.")
    except requests.RequestException as e:
        logger.error(f"Failed to register ESP remotely: {e}")
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Provision ESP32 and register with remote API."
    )
    parser.add_argument(
        "--ca", type=str, default=DEFAULT_CA_PATH, help="Path to CA certificate"
    )
    parser.add_argument(
        "--api-url", type=str, default=DEFAULT_API_URL, help="Remote API endpoint URL"
    )
    parser.add_argument(
        "--token", type=str, required=True, help="Bearer token for API authorization"
    )

    args = parser.parse_args()

    port = find_esp_port()
    if not port:
        logger.error("No ESP32 device found over USB.")
        return

    logger.info(f"Found ESP32 on port: {port}")

    mac = read_mac(port)
    if not mac:
        logger.error("Unable to read MAC address.")
        return
    logger.info(f"Device MAC: {mac}")

    secret = generate_secret()
    logger.info(f"Generated device secret: {secret[:16]}...")

    logger.info("Preparing files for SPIFFS...")
    prepare_files(mac, secret, args.ca)

    logger.info("Creating SPIFFS image...")
    create_spiffs_image()

    logger.info("Flashing SPIFFS image to ESP32...")
    flash_spiffs(port)

    logger.info("Registering ESP in backend...")
    register_device_remotely(mac, secret, args.api_url, args.token)

    logger.info("Provisioning complete.")


if __name__ == "__main__":
    main()
