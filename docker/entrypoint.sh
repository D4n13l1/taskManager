#!/bin/bash
set -e

echo "Waiting for database..."
sleep 2

echo "Running migrations..."
alembic upgrade head || echo "Migration failed or already up to date"

echo "Starting application..."
exec gunicorn main:app -w ${WORKERS:-4} -k uvicorn.workers.UvicornWorker --bind ${HOST:-0.0.0.0}:${PORT:-8000} --timeout 30 --max-requests 1000