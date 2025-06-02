#!/bin/bash

PROJECT_NAME=awecount
DB_SERVICE=database

# Source environment variables from .env file
if [ -f .env ]; then
    source .env
fi

# Connect to the database container and open psql shell
docker compose -p "$PROJECT_NAME" exec -e PGPASSWORD="${POSTGRES_PASSWORD:-awecount}" $DB_SERVICE psql \
    -U "${POSTGRES_USER:-awecount}" \
    -d "${POSTGRES_DATABASE:-awecount}" \
    -h "${POSTGRES_HOST:-database}" \
    -p "${POSTGRES_PORT:-5432}"
