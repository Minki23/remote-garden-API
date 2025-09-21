#!/bin/bash
set -e

echo "Formatting code with Black..."

black . --line-length 100 --exclude "/.venv|/venv|/__pycache__"

echo "Code formatted."
