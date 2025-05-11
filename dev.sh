#!/bin/sh
set -e

cd app

echo "Creating missing tables (SQLAlchemy)..."
python -m app.db_init

echo "Starting FastAPI..."
exec sh ../prod.sh
