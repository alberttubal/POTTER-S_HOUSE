#!/usr/bin/env bash
set -e

# Wait for DB to be available (host/port from env)
# Supports DATABASE_URL or DB_HOST/DB_PORT
if [ -n "${DB_HOST:-}" ]; then
  echo "Waiting for database ${DB_HOST}:${DB_PORT:-5432}..."
  until nc -z "${DB_HOST}" "${DB_PORT:-5432}"; do
    echo "    retrying in 1s..."
    sleep 1
  done
fi

# Run migrations (safe to re-run)
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static (optional for dev; harmless)
# python manage.py collectstatic --noinput

exec "$@"