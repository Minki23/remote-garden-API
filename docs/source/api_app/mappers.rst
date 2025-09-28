Mappers
=======

The **Mappers** package provides data transformation utilities, converting
database entities into DTOs and vice versa.
These mappers act as an intermediate layer between repositories, services,
and API responses.

Modules included:

- ``agents`` – mapping logic for Agent entities.
- ``devices`` – device-to-DTO conversions.
- ``esp_devices`` – ESP device-specific mappers.
- ``gardens`` – mapping garden models and DTOs.
- ``notifications`` – notification mapping utilities.
- ``readings`` – sensor readings conversions.
- ``users`` – user and user-device mapping.

Documentation
-------------

.. automodule:: api_app.mappers.agents
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: mappers.devices
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: mappers.esp_devices
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: mappers.gardens
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: mappers.notifications
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: mappers.readings
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: mappers.users
   :members:
   :undoc-members:
   :show-inheritance:
