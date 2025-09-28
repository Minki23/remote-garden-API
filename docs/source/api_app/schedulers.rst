Schedulers
==========

The **Schedulers** module is responsible for defining and managing
**scheduled background tasks**.
It integrates with **Celery Beat** and **RedBeat** to run periodic jobs
such as reminders, automated garden actions, or maintenance tasks.

Structure
---------

- ``tasks.py`` – contains Celery task definitions for scheduling.

Responsibilities
----------------

- Define background jobs as Celery tasks.
- Integrate with **Celery Beat** for recurring schedules.
- Use **RedBeat** for dynamic scheduling via Redis.
- Trigger periodic automation workflows (e.g., watering, sensor checks).

Documentation
-------------

.. automodule:: api_app.schedulers.tasks
   :members:
   :undoc-members:
   :show-inheritance:
