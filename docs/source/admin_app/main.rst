Admin App
=========

Overview
--------

The **Admin App** is a developer tool for inspecting and managing the
**Common DB**.
It is built with **FastAPI** and **SQLAdmin**, providing a web-based
administration panel for all main entities of the system.

This app is intended strictly for **internal / development use** and is
not part of the production-facing system.

Features
--------

- Provides a web interface with lists, filtering and detailed views.
- Manages all key entities from the **Common DB**.
- Allows quick validation of data without manual SQL queries.
- Connects to the database using the ``DB_CONNECTION_STRING`` environment variable.

Managed Entities
----------------

The Admin App exposes management views for:

- **Users** – authentication data, Google identity, admin rights,
  refresh tokens.
- **Gardens** – user garden instances, notification settings, automation
  flags.
- **ESP Devices** – physical devices (e.g., ESP32) with MAC addresses
  and certificates.
- **Devices** – logical sensors and actuators linked to ESP devices.
- **Notifications** – system alerts, reminders, user messages.
- **Readings** – time-series measurements from devices.
- **User Devices** – end-user mobile devices with FCM tokens.
- **Agents** – AI-driven garden managers linked to gardens.

Usage
-----

Run the app and open the Admin UI in a browser.
By default, it is available under:

``http://localhost:8000/admin``

``admin_app`` is strictly a **developer tool** for local testing,
debugging, and inspection of the database.
