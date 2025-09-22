FROM debian:stable-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssl bash coreutils && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app/mqtt-server

COPY generate-backend-certs.sh /generate-backend-certs.sh
COPY generate-mqtt-certs.sh /generate-mqtt-certs.sh

RUN chmod +x /*.sh

CMD /bin/bash -c "\
    /generate-mqtt-certs.sh && \
    CLIENT_NAME=mock-client /generate-backend-certs.sh && \
    CLIENT_NAME=backend /generate-backend-certs.sh \
    "
