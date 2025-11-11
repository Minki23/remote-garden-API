#!/bin/bash
set -euo pipefail

CLIENT_NAME="${CLIENT_NAME:?CLIENT_NAME is not set}"

BASE_DIR="${BASE_DIR:-.}"
SERVER_NAME="${SERVER_NAME:-mqtt-broker}"
CLIENT_CERT_VALIDITY_DAYS="${CLIENT_CERT_VALIDITY_DAYS:-365}"
CLIENT_KEY_SIZE="${CLIENT_KEY_SIZE:-2048}"

CA_CERT="$BASE_DIR/certs/ca.crt"
CA_KEY="$BASE_DIR/private/ca.key"
CERTS_DIR="$BASE_DIR/$CLIENT_NAME"

mkdir -p "$CERTS_DIR"

echo "Generating client certificate for: $CLIENT_NAME"
echo "Validity: $CLIENT_CERT_VALIDITY_DAYS days"
echo "Key size: $CLIENT_KEY_SIZE bits"

openssl genrsa -out "$CERTS_DIR/$CLIENT_NAME.key" "$CLIENT_KEY_SIZE"

openssl req -new -key "$CERTS_DIR/$CLIENT_NAME.key" \
    -out "$CERTS_DIR/$CLIENT_NAME.csr" \
    -subj "/CN=$SERVER_NAME"

openssl x509 -req \
    -in "$CERTS_DIR/$CLIENT_NAME.csr" \
    -CA "$CA_CERT" \
    -CAkey "$CA_KEY" \
    -CAcreateserial \
    -out "$CERTS_DIR/$CLIENT_NAME.crt" \
    -days "$CLIENT_CERT_VALIDITY_DAYS" \
    -sha256

# Clean up CSR
rm "$CERTS_DIR/$CLIENT_NAME.csr"

echo "Generated $CLIENT_NAME.key and $CLIENT_NAME.crt in $CERTS_DIR"