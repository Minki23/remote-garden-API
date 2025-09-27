Agent App
=========

Overview
--------

The **Agent App** is an AI-driven microservice responsible for
managing and automating garden tasks.
It acts as a **bridge** between the backend API and physical devices,
executing actions such as watering, heating, or ventilation.

Its main responsibilities:

- Receiving **triggers** from the backend.
- Fetching an **access token** from the backend.
- Using the **Backend Agent Client** to query and control devices.
- Running tasks asynchronously (non-blocking with ``asyncio``).
- Reporting results of actions to logs.

Usage
-----

The Agent App exposes its API under ``/agent`` namespace.
Endpoints can be tested via:

- Swagger UI at: ``http://localhost:8001/docs``
- ReDoc at: ``http://localhost:8001/redoc``

Example workflow:

1. A trigger request is sent to ``/agent/trigger`` with a refresh token.
2. The Agent App exchanges it for an **access token** using the backend.
3. Devices linked to the garden are fetched.
4. The agent executes automation logic (e.g., watering).

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api
   services
   clients
   models
