#!/bin/bash

set -e

SERVER_NAME="${SERVER_NAME:-mqtt-broker}"
CA_VALIDITY_DAYS="${CA_VALIDITY_DAYS:-3650}"
SERVER_CERT_VALIDITY_DAYS="${SERVER_CERT_VALIDITY_DAYS:-365}"
CA_KEY_SIZE="${CA_KEY_SIZE:-4096}"
SERVER_KEY_SIZE="${SERVER_KEY_SIZE:-4096}"
CERT_COUNTRY="${CERT_COUNTRY:-PL}"
CERT_STATE="${CERT_STATE:-LowerSilesia}"
CERT_CITY="${CERT_CITY:-Wroclaw}"
CERT_ORGANIZATION="${CERT_ORGANIZATION:-PWR}"
CERT_ORG_UNIT="${CERT_ORG_UNIT:-IT}"
SERVER_HOSTNAME="${SERVER_HOSTNAME:-localhost}"
SERVER_IP="${SERVER_IP:-192.168.100.3}"
ADDITIONAL_SANS="${ADDITIONAL_SANS:-}"
MOSQUITTO_UID="${MOSQUITTO_UID:-1883}"
MOSQUITTO_GID="${MOSQUITTO_GID:-1883}"
PRIVATE_KEY_PERMS="${PRIVATE_KEY_PERMS:-640}"
PUBLIC_CERT_PERMS="${PUBLIC_CERT_PERMS:-644}"
DIR_PERMS="${DIR_PERMS:-770}"

CA_SUBJECT="/C=$CERT_COUNTRY/ST=$CERT_STATE/L=$CERT_CITY/O=$CERT_ORGANIZATION/OU=$CERT_ORG_UNIT/CN=MQTT-CA"

echo "=== MQTT Server Setup (with ESP32 provisioning) ==="
echo "Server Name: $SERVER_NAME"
echo "CA Validity: $CA_VALIDITY_DAYS days"
echo "Server Cert Validity: $SERVER_CERT_VALIDITY_DAYS days"
echo ""

ls

mkdir -p {certs,private,mosquitto/{certs,data,log}}

if [ ! -f "private/ca.key" ]; then
    echo "1. Generating CA..."
    openssl genrsa -out private/ca.key "$CA_KEY_SIZE"
    openssl req -new -x509 -days "$CA_VALIDITY_DAYS" -key private/ca.key -out certs/ca.crt \
        -subj "$CA_SUBJECT"
    echo "CA generated"
else
    echo "1. CA already exists - skipping"
fi

echo "2. Generating server certificate (with SAN)..."

# Build SAN list dynamically
SAN_LIST="DNS.1 = ${SERVER_NAME}
DNS.2 = ${SERVER_HOSTNAME}
IP.1  = ${SERVER_IP}"

# Add additional SANs if provided
if [ -n "$ADDITIONAL_SANS" ]; then
    COUNTER=3
    IFS=',' read -ra SANS <<< "$ADDITIONAL_SANS"
    for san in "${SANS[@]}"; do
        san=$(echo "$san" | xargs) # trim whitespace
        if [[ "$san" == DNS:* ]]; then
            SAN_LIST="$SAN_LIST
DNS.$COUNTER = ${san#DNS:}"
        elif [[ "$san" == IP:* ]]; then
            SAN_LIST="$SAN_LIST
IP.$COUNTER = ${san#IP:}"
        fi
        ((COUNTER++))
    done
fi

cat > server.cnf <<EOF
[ req ]
default_bits       = $SERVER_KEY_SIZE
prompt             = no
default_md         = sha256
req_extensions     = req_ext
distinguished_name = dn

[ dn ]
C  = $CERT_COUNTRY
ST = $CERT_STATE
L  = $CERT_CITY
O  = $CERT_ORGANIZATION
OU = $CERT_ORG_UNIT
CN = ${SERVER_NAME}

[ req_ext ]
subjectAltName = @alt_names

[ alt_names ]
$SAN_LIST
EOF

openssl genrsa -out private/server.key "$SERVER_KEY_SIZE"
openssl req -new -key private/server.key -out server.csr -config server.cnf
openssl x509 -req -in server.csr -CA certs/ca.crt -CAkey private/ca.key \
    -CAcreateserial -out certs/server.crt -days "$SERVER_CERT_VALIDITY_DAYS" -sha256 \
    -extensions req_ext -extfile server.cnf
rm server.csr server.cnf
echo "Server certificate generated (with SAN)"

echo "3. Copying certificates to Docker..."
cp certs/ca.crt mosquitto/certs/
cp certs/server.crt mosquitto/certs/
cp private/server.key mosquitto/certs/

# Set permissions
chmod "$PRIVATE_KEY_PERMS" private/*.key 2>/dev/null || true
chmod "$PUBLIC_CERT_PERMS" certs/*.crt 2>/dev/null || true
chmod "$PRIVATE_KEY_PERMS" mosquitto/certs/*.key 2>/dev/null || true
chmod "$PUBLIC_CERT_PERMS" mosquitto/certs/*.crt 2>/dev/null || true
chmod "$DIR_PERMS" mosquitto/log
chmod "$DIR_PERMS" mosquitto/data
chown -R "$MOSQUITTO_UID:$MOSQUITTO_GID" mosquitto/

echo "=== Done. Restart Mosquitto to apply new certificates. ==="