MQTT Broker
===========

Overview
--------

The **MQTT Broker** is based on Eclipse Mosquitto.  
It ensures secure TLS-based communication between devices,
services, and agents.  

Features:

- Secure TLS communication on port 8883 
- Authentication via client certificates
- Certificate volumes mounted from the generator
- Persistence for data and logs
- Runs as a restricted user for security

Workflow
--------

1. The **Certificate Generator** runs and creates all required certificates.  
2. The **MQTT Broker** starts, loading its server certificate and CA trust.  
3. Devices (e.g., ESP32) connect to the broker using client certificates.  
4. Backend services also authenticate with their own certificates.  
5. Messages flow securely between devices and services.  

Usage
-----

The broker is part of the IoT system network.  
It requires certificates to be generated first and then
provides a secure channel for communication between all participants.
