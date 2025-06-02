#!/bin/bash

PROJECT_NAME=awecount
SERVICE=backend

# Source environment variables from .env file
if [ -f .env ]; then
    source .env
fi

# TODO Remove ipdb from base project requirements. Install only if this script is run.
# Connect to the backend container and open Django shell
docker compose -p "$PROJECT_NAME" exec $SERVICE uv run manage.py shell
