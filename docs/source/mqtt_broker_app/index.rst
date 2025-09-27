MQTT Broker App
===============

Overview
--------

The **MQTT Broker App** provides a secure message exchange
platform for IoT devices (e.g., ESP32), backend services,
and mock clients.

It is divided into two main components:

- **Certificate Generator** – responsible for creating all TLS certificates.
- **MQTT Broker** – the actual broker, running Eclipse Mosquitto with TLS.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   cert_generator
   mqtt_broker
