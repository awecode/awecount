#!/bin/bash
docker compose -p awecount down
docker volume rm awecount_frontend_dist
git pull origin main
docker compose -p awecount up --build -d

# Zeroish Downtime Restart

# set -euo pipefail

# APP_SERVICES=(frontend backend worker)

# echo "📥 Pulling latest code ..."
# git pull origin main

# echo "🔧 Rebuilding app services only: ${APP_SERVICES[*]} and migrator..."
# docker compose -p "$PROJECT_NAME" build "${APP_SERVICES[@]}" migrator

# echo "📦 Running migrations..."
# docker compose -p "$PROJECT_NAME" run --rm migrator

# echo "🚀 Restarting app services with minimal downtime..."
# docker compose -p "$PROJECT_NAME" up -d --no-deps "${APP_SERVICES[@]}"

# echo "✅ Restart completed at $(date)"

## TODO:
# 1. Test if new changes in frontend is available without having to cleanup the frontend_dist volume.