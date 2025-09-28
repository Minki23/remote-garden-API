CSR Signer App
==============

Overview
--------

The **CSR Signer App** is a FastAPI-based microservice responsible
for signing **Certificate Signing Requests (CSRs)** using a pre-generated
Certificate Authority (CA).

It is typically used to provision certificates for ESP32 devices
or other microservices in the system.
Certificates issued by this service are signed with the CA private key
and are valid for 1 year.

Main responsibilities:

- Accept incoming **PEM-encoded CSRs** via API.
- Validate CSR signatures.
- Issue a signed **X.509 certificate**.
- Ensure certificates are non-CA (`BasicConstraints: CA = False`).

Usage
-----

Start the app (example with uvicorn):

.. code-block:: bash

    uvicorn csr_signer_app.main:app --reload --port 8005

API endpoint:

- ``POST /sign-csr``
  Request body: JSON with CSR PEM string.
  Response: JSON with signed certificate PEM.

Example request:

.. code-block:: json

    {
      "csr_pem": "-----BEGIN CERTIFICATE REQUEST-----\nMIIC..."
    }

Example response:

.. code-block:: json

    {
      "cert": "-----BEGIN CERTIFICATE-----\nMIIC..."
    }

Python API
----------

Main Application
----------------

.. automodule:: csr_signer_app.main
   :members:
   :undoc-members:
   :show-inheritance:
