#!/bin/bash
set -e

trap 'rm -f spiffs.bin spiffs_data' EXIT

TOKEN=$1
PORT=${PORT:-/dev/ttyUSB0}
URL=http://localhost:3000/api/admin/esp/create

if [ -z "$TOKEN" ]; then
  echo "Usage: $0 <token>"
  exit 1
fi

# Utwórz katalog jeśli nie istnieje
mkdir -p spiffs_data

echo "[1/4] Read MAC from esp at $PORT..."
MAC=$(docker run --rm --device=${PORT}:${PORT} espressif/idf:latest \
  esptool.py --chip esp32 --port ${PORT} read_mac 2>/dev/null \
  | grep "MAC:" \
  | awk '{print $2}' \
  | tr -d ':' \
  | head -n 1)

if [ -z "$MAC" ]; then
  echo "Cannot read MAC address"
  exit 1
fi
echo "MAC: $MAC"

echo "[2/4] Registerig and files preparation..."
docker run --rm --network host \
  -v $(pwd)/spiffs_data:/app/spiffs_data \
  python-prepare-esp \
  --token "$TOKEN" --mac "$MAC" --api-url "$URL"

# Sprawdź czy pliki zostały utworzone
if [ ! -d "spiffs_data" ] || [ -z "$(ls -A spiffs_data 2>/dev/null)" ]; then
  echo "No SPIFFS data created! Check API connection and credentials."
  exit 1
fi

echo "[3/4] Building SPIFFS image..."
docker run --rm \
  -v $(pwd)/spiffs_data:/data \
  -v $(pwd):/output \
  espressif/idf:latest \
  bash -c "
    cd /tmp && \
    wget -q https://github.com/igrr/mkspiffs/releases/download/0.2.3/mkspiffs-0.2.3-arduino-esp32-linux64.tar.gz && \
    tar -xzf mkspiffs-*.tar.gz && \
    MKSPIFFS=\$(find . -name 'mkspiffs' -type f | head -1) && \
    chmod +x \$MKSPIFFS && \
    \$MKSPIFFS -c /data -b 4096 -p 256 -s 393216 /output/spiffs.bin
  "

echo "[4/4] ESP32 flashing..."
docker run --rm --device=${PORT}:${PORT} -v $(pwd):/work espressif/idf:latest \
  esptool.py --chip esp32 --port ${PORT} --baud 460800 write_flash 0x220000 /work/spiffs.bin

echo "Ready!!"