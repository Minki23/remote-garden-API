#!/bin/bash

exec uvicorn main:app --reload --host 0.0.0.0 --port 3000 --log-level debug
