#!/usr/bin/env bash
set -e

# Wait for database
uv run manage.py wait_for_db

# Wait for migrations
uv run manage.py wait_for_migrations

# Run processes
uv run manage.py qcluster
