Migrations
==========

The **Migrations** module contains the database migration scripts
managed by **Alembic**.
It is responsible for tracking changes in the database schema
over time and ensuring smooth upgrades and downgrades.

Contents
--------

- ``env.py`` – Alembic environment configuration, setting up the context
  for migrations (database connection, metadata).
- ``script.py.mako`` – template used for generating new migration scripts.
- ``versions/`` – directory containing actual migration scripts,
  each named with a unique revision identifier.
- ``README`` – description of the Alembic environment.
