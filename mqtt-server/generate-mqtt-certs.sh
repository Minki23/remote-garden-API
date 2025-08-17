#!/bin/bash

set -e

SERVER_IP="192.168.100.3"
CA_SUBJECT="/C=PL/ST=LowerSilesia/L=Wroclaw/O=PWR/OU=IT/CN=MQTT-CA"
SERVER_SUBJECT="/C=PL/ST=LowerSilesia/L=Wroclaw/O=PWR/OU=IT/CN=${SERVER_IP}"

echo "=== MQTT Server Setup (with ESP32 provisioning) ==="
echo "Server IP: $SERVER_IP"
echo ""

mkdir -p {certs,private,mosquitto/{certs,data,log}}

if [ ! -f "private/ca.key" ]; then
    echo "1. Generating CA..."
    openssl genrsa -out private/ca.key 4096
    openssl req -new -x509 -days 3650 -key private/ca.key -out certs/ca.crt \
        -subj "$CA_SUBJECT"
    echo "CA generated"
else
    echo "1. CA already exists - skipping"
fi

echo "2. Generating server certificate..."
openssl genrsa -out private/server.key 4096
openssl req -new -key private/server.key -out server.csr \
    -subj "$SERVER_SUBJECT"
openssl x509 -req -in server.csr -CA certs/ca.crt -CAkey private/ca.key \
    -CAcreateserial -out certs/server.crt -days 365
rm server.csr
echo "Server certificate generated"

echo "3. Copying certificates to Docker..."
cp certs/ca.crt mosquitto/certs/
cp certs/server.crt mosquitto/certs/  
cp private/server.key mosquitto/certs/

chmod 600 private/*.key mosquitto/certs/*.key 2>/dev/null || true
chmod 644 certs/*.crt mosquitto/certs/*.crt 2>/dev/null || true
sudo chown -R 1883:1883 mosquitto/ 2>/dev/null || chown -R 1883:1883 mosquitto/
