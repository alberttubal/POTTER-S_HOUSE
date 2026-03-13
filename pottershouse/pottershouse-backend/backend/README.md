# Backend README

## Overview
Django REST API for Potter's House. All endpoints are under /api/v1.

## Requirements
- Python 3.12+
- PostgreSQL 13+
- Redis 7+
- S3-compatible storage (AWS S3 / MinIO)

## Local Setup
1. Create and activate venv
2. Install requirements
3. Copy .env.example to .env and fill values
4. Run migrations
5. Start server

## Key Environment Variables
- DJANGO_SECRET_KEY
- DATABASE_URL
- REDIS_HOST, REDIS_PORT
- AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME
- IDEMPOTENCY_TTL
- ENABLE_METRICS
- PAGERDUTY_ROUTING_KEY

## Migrations
```powershell
python manage.py migrate
```

## Tests
```powershell
python manage.py test --settings=backend.settings.test
```

## Workers
```powershell
celery -A backend worker -l info
celery -A backend beat -l info
```
