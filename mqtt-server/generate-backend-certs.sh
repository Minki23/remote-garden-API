#!/bin/bash
set -euo pipefail

BASE_DIR="."
CA_CERT="$BASE_DIR/certs/ca.crt"
CA_KEY="$BASE_DIR/private/ca.key"
CERTS_DIR="$BASE_DIR/backend"
SERVER_NAME="mqtt-broker"

mkdir -p "$CERTS_DIR"

openssl genrsa -out "$CERTS_DIR/backend.key" 2048

openssl req -new -key "$CERTS_DIR/backend.key" \
    -out "$CERTS_DIR/backend.csr" \
    -subj "/CN=$SERVER_NAME"

openssl x509 -req \
    -in "$CERTS_DIR/backend.csr" \
    -CA "$CA_CERT" \
    -CAkey "$CA_KEY" \
    -CAcreateserial \
    -out "$CERTS_DIR/backend.crt" \
    -days 365 \
    -sha256

echo "Generated backend.key and backend.crt in $CERTS_DIR"
