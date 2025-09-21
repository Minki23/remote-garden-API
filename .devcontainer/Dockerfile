FROM mcr.microsoft.com/devcontainers/python:3.11

RUN apt-get update && apt-get install -y --no-install-recommends \
    git build-essential pkg-config libffi-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspaces
