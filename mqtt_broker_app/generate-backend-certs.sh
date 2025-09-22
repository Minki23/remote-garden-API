#!/bin/bash
set -euo pipefail

CLIENT_NAME="${CLIENT_NAME:?CLIENT_NAME is not set}"

BASE_DIR="."
CA_CERT="$BASE_DIR/certs/ca.crt"
CA_KEY="$BASE_DIR/private/ca.key"
CERTS_DIR="$BASE_DIR/$CLIENT_NAME"
SERVER_NAME="mqtt-broker"

mkdir -p "$CERTS_DIR"

openssl genrsa -out "$CERTS_DIR/$CLIENT_NAME.key" 2048

openssl req -new -key "$CERTS_DIR/$CLIENT_NAME.key" \
    -out "$CERTS_DIR/$CLIENT_NAME.csr" \
    -subj "/CN=$SERVER_NAME"

openssl x509 -req \
    -in "$CERTS_DIR/$CLIENT_NAME.csr" \
    -CA "$CA_CERT" \
    -CAkey "$CA_KEY" \
    -CAcreateserial \
    -out "$CERTS_DIR/$CLIENT_NAME.crt" \
    -days 365 \
    -sha256

echo "Generated $CLIENT_NAME.key and $CLIENT_NAME.crt in $CERTS_DIR"
