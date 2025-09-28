Mock MQTT Device
================

Overview
--------

The **Mock MQTT Device** is a developer tool used to simulate an ESP-based IoT device.
It connects to the **MQTT Broker** over TLS using client certificates, publishes fake sensor data,
receives control commands, and responds with confirmations.

This tool allows developers to test the **full IoT pipeline** without requiring real hardware.
It is especially useful for validating backend integration, device provisioning,
and automation logic.

Responsibilities
----------------

- Connect securely to the broker using TLS certificates.
- Announce device presence with connection and status messages.
- Simulate multiple sensors (light, humidity, temperature, soil moisture, etc.).
- React to control commands (e.g., water on/off, fan on/off).
- Publish confirmation messages when actions are executed.
- Send periodic heartbeat to signal that the device is online.

Usage
-----

1. **Run the container** with proper certificates mounted:
   - `ca.crt`, `mock-client.crt`, `mock-client.key`
2. Set environment variables:
   - ``DEVICE_MAC`` – unique device identifier.
   - ``USER_KEY`` – user authentication key.
3. The mock device will automatically:
   - Connect to the broker.
   - Start publishing random sensor readings.
   - Listen for control messages.
   - Confirm received actions.

Workflow
--------

- On startup:
  - Connects to broker ``mqtt-broker:8883``.
  - Subscribes to ``<DEVICE_MAC>/device/control``.
  - Publishes initial connection info and online status.

- During operation:
  - Publishes sensor data to ``<DEVICE_MAC>/device/sensor``.
  - Sends online heartbeat every 30 seconds.
  - Listens for control actions and updates device state.
  - Sends confirmations on ``<DEVICE_MAC>/device/confirm``.

Purpose
-------

The **Mock MQTT Device** is intended **only for development and testing**.
It enables the system to be validated end-to-end without requiring real ESP32 hardware.
This makes it easier to iterate on backend services, automation agents,
and broker configuration.

