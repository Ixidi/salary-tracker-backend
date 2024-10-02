#!/bin/bash

docker run --rm \
  -v "$(pwd)/requirements.in:/app/requirements.in" \
  -v "$(pwd):/app" \
  python:3.12.6 \
  sh -c "cd /app && pip install pip-tools && pip-compile requirements.in > requirements.txt"