#!/usr/bin/env bash

set -e

# Wait for database
uv run manage.py wait_for_db

# Wait for migrations
uv run manage.py wait_for_migrations

# Run processes
uv run gunicorn -w "${GUNICORN_WORKERS:-1}" -k uvicorn.workers.UvicornWorker awecount.asgi:application --bind 0.0.0.0:"${PORT:-8000}" --max-requests 1200 --max-requests-jitter 1000 --access-logfile -
