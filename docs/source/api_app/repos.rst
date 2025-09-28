Repositories
============

The **Repositories** module contains classes responsible for
**database access and persistence**.
They encapsulate SQLAlchemy logic and provide a clean interface
to the **Service layer**, ensuring separation of concerns.

Structure
---------

- ``agents.py`` – repository for agent entities.
- ``devices.py`` – repository for devices.
- ``esp_devices.py`` – repository for ESP devices.
- ``gardens.py`` – repository for gardens.
- ``notifications.py`` – repository for notifications.
- ``readings.py`` – repository for sensor readings.
- ``schedules.py`` – repository for schedules.
- ``user_device.py`` – repository for user-to-device assignments.
- ``users.py`` – repository for user accounts.
- ``utils/super_repo.py`` – base repository with shared CRUD utilities.

Responsibilities
----------------

- Querying database entities.
- Performing CRUD operations.
- Returning ORM models to the **Service layer**.
- Abstracting raw SQLAlchemy usage from business logic.

Notes
-----

- Each repository corresponds to a domain entity.
- Common functionality is shared in ``SuperRepo``.
- Repositories never contain business logic, only **data access**.

DTOs
----

Repositories frequently interact with **DTOs** (Data Transfer Objects)
from the :doc:`models` module. DTOs define the schema of data exchanged
between layers and ensure validation.


Documentation
-------------

.. automodule:: api_app.repos.agents
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: api_app.repos.devices
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: api_app.repos.esp_devices
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: api_app.repos.gardens
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: api_app.repos.notifications
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: api_app.repos.readings
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: api_app.repos.schedules
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: api_app.repos.user_device
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: api_app.repos.users
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: api_app.repos.utils.super_repo
   :members:
   :undoc-members:
   :show-inheritance:
