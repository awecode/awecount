#!/bin/bash
set -e
# Wait for database
python manage.py wait_for_db

# Wait for migrations
python manage.py wait_for_migrations

# Run processes
exec gunicorn -w "$GUNICORN_WORKERS" -k uvicorn.workers.UvicornWorker awecount.asgi:application --bind 0.0.0.0:"${PORT:-8000}" --max-requests 1200 --max-requests-jitter 1000 --access-logfile -
