#!/usr/bin/env bash
set -e

echo "=== ReviewAI Database Migration Runner ==="

# Wait for PostgreSQL database to accept connections
echo "Checking database connectivity..."
until docker exec reviewai_db_prod pg_isready -U reviewai -d reviewai_db > /dev/null 2>&1; do
    echo "Waiting for PostgreSQL database container..."
    sleep 2
done

echo "Running Alembic migrations..."
docker exec reviewai_backend_prod alembic upgrade head

echo "=== Database Migrations Applied Successfully ==="
