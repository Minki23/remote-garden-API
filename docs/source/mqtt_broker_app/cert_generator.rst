Certificate Generator
=====================

Overview
--------

The **Certificate Generator** prepares all certificates
required for secure MQTT communication.

It is built as a separate container that runs before the broker
and generates:

- **CA (Certificate Authority)** – root of trust for all components.
- **Server certificate** – used by the MQTT Broker.
- **Client certificates** – for backend and mock/test clients.

Workflow
--------

1. On startup, the generator checks if a CA already exists.
   - If not, it creates a new CA.
2. A server certificate with SAN (Subject Alternative Names) is issued.
3. Individual client certificates are generated for each required client.
4. Certificates and keys are placed in shared volumes, available to the broker.

Usage
-----

The generator runs automatically as part of the system startup.
It does not run persistently but only produces certificates
and then exits successfully.
