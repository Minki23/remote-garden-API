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

1. **CA Initialization**

   - On startup, the generator checks if the CA already exists
     (``private/ca.key`` and ``certs/ca.crt``).
   - If not, a new **4096-bit RSA key** is created along with a
     **self-signed CA certificate** valid for 10 years.
   - The CA subject includes:
     
     - ``/C=PL/ST=LowerSilesia/L=Wroclaw/O=PWR/OU=IT/CN=MQTT-CA``

2. **Server Certificate Issuance**

   - A **4096-bit RSA server key** is generated.
   - A **CSR (Certificate Signing Request)** is prepared with
     distinguished name values and **Subject Alternative Names (SAN)**:
     
     - ``DNS: mqtt-broker``
     - ``IP: 192.168.100.3``
   
   - The CSR is signed by the CA, producing the server certificate
     (``certs/server.crt``).
   - The certificate is valid for one year and uses **SHA-256**.

3. **Client Certificate Provisioning**

   - For each client (provided via the ``CLIENT_NAME`` variable),
     the generator script:
     
     - creates a **2048-bit RSA key** (``<CLIENT_NAME>.key``),
     - generates a CSR with ``/CN=mqtt-broker``,
     - signs it with the CA to issue the client certificate
       (``<CLIENT_NAME>.crt``).
   
   - Certificates and keys are stored in a dedicated directory
     (``./<CLIENT_NAME>``).

4. **Certificate Distribution**

   - The generated certificates and keys are copied to
     ``mosquitto/certs/`` and shared volumes.
   - File permissions are tightened:
     
     - ``*.key`` files restricted to the owner (read/write),
     - ``*.crt`` certificates readable by all,
     - data and log directories writable only by the Mosquitto user
       (UID ``1883``).

Usage
-----

The generator runs automatically as part of the system startup.

- It **does not run persistently** – it only creates the required
  certificates and exits successfully.
- Certificates are then available to the MQTT Broker and to all
  provisioned clients (e.g., ESP32 devices, backend services).
