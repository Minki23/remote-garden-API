Scripts
=======

The **Scripts** directory contains helper shell and Python scripts used to
manage and maintain the project during development and testing.

Contents
--------

- ``migration_manager.sh``
  Manage Alembic database migrations (generate, apply, revert).

- ``mock_data.py``
  Generate mock users, gardens, ESP devices, sensors, readings, and notifications
  in the database for testing and development.

- ``run_cam_bind.sh``
  Bind an external RTSP camera stream to a local RTSP server using **ffmpeg**.
  Requires **mediamtx** to be running.

- ``websocket_connection.sh``
  Connect to the WebSocket API (``/ws/wsinit``) using **wscat**, with optional
  authentication token.

Documentation
-------------

.. automodule:: api_app.utils.scripts.mock_data
   :members:
   :undoc-members:
   :show-inheritance:
