#!/bin/bash
set -e

# Wait for database
python manage.py wait_for_db

# Wait for migrations
python manage.py wait_for_migrations

# Run processes
python manage.py q-cluster
