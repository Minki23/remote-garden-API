API App
=======

Overview
--------

The **API App** is the central backend microservice of the Garden Management
System. It provides REST, WebSocket, and MQTT interfaces that allow
users, devices, and agents to communicate securely.

It is built with **FastAPI**, follows a layered architecture
(controllers → services → repositories → database), and integrates
with external systems such as:

- **PostgreSQL** for relational data storage.
- **Redis + Celery** for background tasks and scheduling.
- **Eclipse Mosquitto (MQTT)** for real-time device communication.
- **Firebase** for push notifications.
- **TLS certificates** for secure device and backend communication.

Main responsibilities
---------------------

- **User & Authentication Management**
  - JWT-based authentication and Google login.
  - Admin and standard user flows.

- **Garden & Device Management**
  - CRUD for gardens, devices, and ESP32-based IoT units.
  - Linking users with their devices.

- **Data & Readings**
  - Collecting sensor values (soil moisture, light, temperature).
  - Storing and querying device readings.

- **Scheduling & Automation**
  - Managing scheduled garden actions (watering, heating, atomization).
  - Running Celery periodic tasks with **RedBeat** scheduler.

- **Notifications**
  - Sending push notifications via Firebase.
  - Handling in-app notifications.

- **MQTT Integration**
  - Subscribing to device status and readings.
  - Publishing actuator commands.
  - Handling TLS-secured communication.

- **Live Communication**
  - Real-time streaming (WebSocket, camera).
  - Bidirectional device-backend updates.


Example workflow
----------------

1. A user logs in and registers their garden and devices.
2. An ESP32 device connects to MQTT broker using TLS certificates.
3. Sensor readings are published to MQTT and stored in the database.
4. A scheduled watering task is triggered via Celery.
5. The API App publishes an MQTT actuator command to the device.
6. The device confirms execution, and a push notification is sent to the user.

Documentation structure
-----------------------

.. toctree::
   :maxdepth: 2
   :caption: Modules:

   main
   core
   controllers
   clients
   services
   repos
   models
   mappers
   exceptions
   migrations
   schedulers
   views
   templates
   static
   utils