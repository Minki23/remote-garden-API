Services
========

The **Services** module implements the **business logic layer** of the application.
It orchestrates data flow between the **Controllers**, **Repositories**, and external **Clients**.

Structure
---------

- ``agents.py`` – logic for managing agents.
- ``auth.py`` – authentication and authorization services.
- ``camera.py`` – camera and streaming services.
- ``devices.py`` – device-related business logic.
- ``esp_devices.py`` – ESP device management.
- ``gardens.py`` – garden domain services.
- ``notifications.py`` – notification delivery logic.
- ``readings.py`` – handling sensor readings.
- ``schedules.py`` – task scheduling services.
- ``user_devices.py`` – services for user-to-device relations.
- ``users.py`` – user account management.

Responsibilities
----------------

- Encapsulate **business rules** and workflows.
- Act as a bridge between **Repositories** (data access) and **Controllers** (API).
- Contain validation and orchestration logic.
- Ensure **separation of concerns** between persistence and presentation layers.

Documentation
-------------

.. automodule:: api_app.services.agents
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: api_app.services.auth
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: api_app.services.camera
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: api_app.services.devices
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: api_app.services.esp_devices
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: api_app.services.gardens
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: api_app.services.notifications
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: api_app.services.readings
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: api_app.services.schedules
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: api_app.services.user_devices
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: api_app.services.users
   :members:
   :undoc-members:
   :show-inheritance:
