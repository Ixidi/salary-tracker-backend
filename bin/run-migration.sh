#!/bin/bash

docker compose -f docker/docker-compose.yml run --rm \
  -v "$(pwd):/app" \
  backend \
  sh -c "cd /app && alembic upgrade head"