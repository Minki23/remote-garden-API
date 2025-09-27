Delivery App
============

The ``delivery_app`` module is the orchestration and infrastructure layer of
the Remote Garden system. Its primary role is to define, configure, and start
all required microservices that together form the ecosystem.

Unlike other applications (``agent_app`` or ``api_app``), this module does not
implement business logic itself. Instead, it provides a **deployment-ready
environment** where all services can run, communicate securely, and be tested
as a single unit.

Purpose
-------

The purpose of ``delivery_app`` can be summarized in the following points:

- **Infrastructure orchestration** – start and stop all dependent services
  such as the API, the Agent, database, message broker, workers, and more.
- **Reproducibility** – provide a Docker Compose-based environment that
  ensures the entire system can be bootstrapped on any machine with a single command.
- **Security** – integrate with the certificate authority (CSR signer) to
  generate and manage TLS certificates for secure device-to-cloud communication.
- **Developer support** – offer additional tools such as the Admin Panel
  and Mock MQTT Publisher for debugging, inspection, and testing without
  requiring physical devices.
- **Production readiness** – prepare the ground for deploying the Remote Garden
  system into a real environment by combining all critical services into
  a stable and scalable setup.

Core Responsibilities
---------------------

``delivery_app`` takes care of the following system-wide responsibilities:

1. **Service Orchestration**
   - Define and run Docker containers for the API, Agent, PostgreSQL, Redis,
     Celery, MQTT broker, and certificate authority.
   - Ensure dependencies are resolved in the correct startup order.

2. **Networking**
   - Configure container networking to allow services to reach each other
     securely via internal Docker networks.
   - Expose public ports only when required (e.g., API, MQTT).

3. **Security and Certificates**
   - Include the CSR Signer service, which acts as a lightweight
     certificate authority.
   - Provide runtime certificate generation for ESP devices to establish
     mutual TLS with the MQTT broker.

4. **Task Management**
   - Run Celery workers and the Celery beat scheduler for background
     tasks, automations, and reminders.
   - Ensure reliable event-driven communication through Redis.

5. **Monitoring and Debugging (Development Mode)**
   - Provide an Admin Panel service that connects to the database and
     allows developers to inspect data directly.
   - Include a Mock MQTT Publisher that simulates ESP-based garden devices,
     which is particularly useful for integration testing when hardware
     is unavailable.

Included Components
-------------------

The following services are orchestrated by ``delivery_app``:

- **API Service (``api_app``)**
  Handles core business logic, user management, gardens, devices,
  readings, schedules, and notifications.

- **Agent Service (``agent_app``)**
  An intelligent agent that manages the garden by executing schedules,
  triggering actions, and making automated decisions.

- **Database (PostgreSQL)**
  Stores all persistent information: users, devices, gardens, readings,
  schedules, notifications, and authentication tokens.

- **Redis**
  Provides in-memory caching and acts as a Celery message broker.

- **Celery Workers and Scheduler**
  Run asynchronous and periodic tasks such as sending notifications,
  executing scheduled actions, and processing background jobs.

- **MQTT Broker**
  Manages communication between ESP devices and the cloud. It is secured
  using TLS certificates to prevent unauthorized access.

- **CSR Signer**
  Issues TLS client certificates for ESP devices, allowing them to securely
  authenticate with the MQTT broker.

- **Admin Panel (Developer Tool)**
  A web-based interface to inspect and query the database. This tool is not
  required in production but is extremely useful during development.

- **Mock MQTT Publisher (Developer Tool)**
  A simulator for ESP devices that publishes synthetic sensor readings and
  listens for control actions. It enables local testing without the need
  for physical IoT hardware.

Usage
-----

The project provides a top-level ``Makefile`` located one directory above
``delivery_app``. This Makefile centralizes the workflow for building,
pushing, deploying, and running all microservices in the system.

Typical usage:

- **Build a single service**

  .. code-block:: bash

     make build SERVICE=agent_app REGISTRY=my-docker-org TAG=v1.0

- **Push a single service image**

  .. code-block:: bash

     make push SERVICE=agent_app

- **Build and push all services**

  .. code-block:: bash

     make deploy-all REGISTRY=my-docker-org TAG=latest

- **Run the full system via Docker Compose**

  .. code-block:: bash

     make run

- **Run in detached (background) mode**

  .. code-block:: bash

     make run-detached

- **Stop all running services**

  .. code-block:: bash

     make stop

- **Clean up images and resources**

  .. code-block:: bash

     make clean-images
     make clean

The Makefile also provides a ``help`` target that lists all available
commands and environment variables:

.. code-block:: bash

   make help


Conclusion
----------

``delivery_app`` is the backbone of the Remote Garden ecosystem. While it
does not contain business rules or models itself, it guarantees that all
other services can run in harmony, communicate reliably, and be deployed
reproducibly. Its design bridges the gap between development convenience
and production readiness, making it indispensable for both developers
and system operators.
