Models (DTOs)
=============

The **Models** module contains all **Data Transfer Objects (DTOs)** 
used across the API.
They define the **request and response schemas** and are built with 
**Pydantic** for validation and serialization.

DTOs ensure that request/response formats are consistent and 
validated automatically across the system.

Structure
---------

- ``admin.py`` – DTOs for administrative actions.
- ``agents.py`` – DTOs for agents.
- ``auth.py`` – authentication and token handling models.
- ``devices.py`` – device-related DTOs.
- ``esp_device.py`` – DTOs for ESP32 devices.
- ``gardens.py`` – garden management schemas.
- ``google_login.py`` – Google OAuth login DTOs.
- ``notifications.py`` – notification payloads.
- ``readings.py`` – sensor reading models.
- ``schedules.py`` – scheduling structures.
- ``status.py`` – system/device status DTOs.
- ``user_devices.py`` – user-to-device linking DTOs.
- ``users.py`` – user account DTOs.


Documentation
-------------

.. automodule:: api_app.models.dtos.admin
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: api_app.models.dtos.agents
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: api_app.models.dtos.auth
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: api_app.models.dtos.devices
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: api_app.models.dtos.esp_device
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: api_app.models.dtos.gardens
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: api_app.models.dtos.google_login
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: api_app.models.dtos.notifications
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: api_app.models.dtos.readings
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: api_app.models.dtos.schedules
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: api_app.models.dtos.status
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: api_app.models.dtos.user_devices
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: api_app.models.dtos.users
   :members:
   :undoc-members:
   :show-inheritance:
