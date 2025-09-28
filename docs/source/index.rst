Greenhouse Remote Management System
===================================

This is documentation of the **Greenhouse Remote Management System**.
The project enables both **automatic** and **manual** control of greenhouse conditions through **web** and **mobile** applications.

The main goal is to provide the user with **remote control** over processes such as:

- irrigation,
- monitoring temperature and humidity,
- managing ventilation and lighting,
- real-time camera feed.

The system is based on an **ESP32** microcontroller connected to sensors and actuators, which collect data and control greenhouse devices, communicating with the backend and client applications.

.. contents:: Table of Contents
   :local:
   :depth: 2

System Overview
---------------

The backend is designed as part of a **modular microservices ecosystem** that powers the Greenhouse Remote Management System.
While the ESP32 devices and client applications handle hardware interaction and user interfaces, the backend provides the **core logic and integration layer**.

The Python backend consists of several key components:

- **API App** – main application providing REST API endpoints for managing users, gardens, devices, and schedules.
- **Agent App** – communication layer for greenhouse agents interacting with sensor data and actuators.
- **Admin App** – administrative panel for managing users, devices, and system configuration.
- **Certificate Signer App** – responsible for dynamic provisioning and PKI-based device authentication.
- **MQTT Broker** – responsible for communication with ESP devices.
- **Supporting Services** – including MQTT broker integration, task scheduling, and notification handling.

.. note::

   TODO: Add a **backend architecture diagram** here
   e.g. ``.. image:: _static/backend_architecture.png`` to illustrate service-to-service communication.

Scope of the Project
--------------------

The Backend and API scope of project includes:

- REST API for greenhouse management,
- scheduling and task automation via Celery + Redis,
- MQTT broker with TLS authentication,
- MQTT integration for communication with devices,
- user authentication and role-based access control,
- certificate generation and device provisioning,
- AI agent module to operate automatically with devices,
- system documentation generated with Sphinx
- infrastructure tools to manage the project lifespam and its delivery

Documentation Structure
-----------------------

The documentation is organized according to the applications that make up the system:

.. toctree::
   :maxdepth: 2
   :caption: Applications

   admin_app/main
   agent_app/index
   api_app/index
   common_db/index
   csr_signer_app/main
   delivery_app/main
   mqtt_broker_app/index
   mock_mqtt_app/main
