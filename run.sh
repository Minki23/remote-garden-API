#!/usr/bin/env bash
set -e

docker compose --profile prod up --build --force-recreate "$@"
