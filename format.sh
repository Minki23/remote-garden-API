#!/bin/bash
set -e

VENV=".black_venv"
python3 -m venv "$VENV"
source "$VENV/bin/activate"
pip install -q black

black . --line-length 100 --exclude "$VENV" || true

deactivate
rm -rf "$VENV"

echo "Code formatted with Black (line length = 100)."
