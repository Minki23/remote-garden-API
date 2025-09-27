#!/bin/bash

set -e

SERVER_NAME="mqtt-broker"
CA_SUBJECT="/C=PL/ST=LowerSilesia/L=Wroclaw/O=PWR/OU=IT/CN=MQTT-CA"

echo "=== MQTT Server Setup (with ESP32 provisioning) ==="
echo "Server Name: $SERVER_NAME"
echo ""

ls

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

echo "2. Generating server certificate (with SAN)..."

cat > server.cnf <<EOF
[ req ]
default_bits       = 4096
prompt             = no
default_md         = sha256
req_extensions     = req_ext
distinguished_name = dn

[ dn ]
C  = PL
ST = LowerSilesia
L  = Wroclaw
O  = PWR
OU = IT
CN = ${SERVER_NAME}

[ req_ext ]
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = ${SERVER_NAME}
IP.1  = 192.168.100.3
EOF

openssl genrsa -out private/server.key 4096
openssl req -new -key private/server.key -out server.csr -config server.cnf
openssl x509 -req -in server.csr -CA certs/ca.crt -CAkey private/ca.key \
    -CAcreateserial -out certs/server.crt -days 365 -sha256 \
    -extensions req_ext -extfile server.cnf
rm server.csr server.cnf
echo "Server certificate generated (with SAN)"

echo "3. Copying certificates to Docker..."
cp certs/ca.crt mosquitto/certs/
cp certs/server.crt mosquitto/certs/
cp private/server.key mosquitto/certs/

# sudo chown -R vscode:1883 mosquitto/ 2>/dev/null || chown -R vscode:1883 mosquitto/
chmod 640 private/*.key 2>/dev/null || true
chmod 644 certs/*.crt 2>/dev/null || true
chmod 640 mosquitto/certs/*.key 2>/dev/null || true
chmod 644 mosquitto/certs/*.crt 2>/dev/null || true
chmod 770 mosquitto/log
chmod 770 mosquitto/data
chown -R 1883:1883 mosquitto/

echo "=== Done. Restart Mosquitto to apply new certificates. ==="
