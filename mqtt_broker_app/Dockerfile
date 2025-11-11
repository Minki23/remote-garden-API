FROM debian:stable-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssl bash coreutils && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app/mqtt-server

COPY ./mqtt_broker_app/generate-backend-certs.sh /generate-backend-certs.sh
COPY ./mqtt_broker_app/generate-mqtt-certs.sh /generate-mqtt-certs.sh

RUN chmod +x /*.sh

ENV CA_VALIDITY_DAYS=3650 \
    SERVER_CERT_VALIDITY_DAYS=365 \
    CLIENT_CERT_VALIDITY_DAYS=365 \
    CA_KEY_SIZE=4096 \
    SERVER_KEY_SIZE=4096 \
    CLIENT_KEY_SIZE=2048 \
    CERT_COUNTRY=PL \
    CERT_STATE=LowerSilesia \
    CERT_CITY=Wroclaw \
    CERT_ORGANIZATION=PWR \
    CERT_ORG_UNIT=IT \
    SERVER_NAME=mqtt-broker \
    SERVER_HOSTNAME=vps-2505986b.vps.ovh.net \
    SERVER_IP=192.168.100.3 \
    ADDITIONAL_SANS="" \
    BASE_DIR=. \
    MOSQUITTO_UID=1883 \
    MOSQUITTO_GID=1883 \
    PRIVATE_KEY_PERMS=640 \
    PUBLIC_CERT_PERMS=644 \
    DIR_PERMS=770

CMD /bin/bash -c "\
    /generate-mqtt-certs.sh && \
    CLIENT_NAME=mock-client /generate-backend-certs.sh && \
    CLIENT_NAME=backend /generate-backend-certs.sh \
    "