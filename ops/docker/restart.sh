#!/bin/bash
docker compose down
docker volume rm awecount_frontend_dist
git pull origin main
docker compose up --build -d