#!/bin/bash 

set -e

echo "Creating missing tables (SQLAlchemy)..."
python -m app.db_init

echo "Starting FastAPI..."
exec bash ../prod.sh
