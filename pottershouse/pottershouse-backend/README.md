# Potters House - Backend 
 
Production-ready Django REST API for Potters House. All endpoints are under `/api/v1`. 
 
## Requirements 
- Python 3.12+ (3.13 works locally) 
- PostgreSQL 13+ 
- Redis 7+ 
- MinIO or AWS S3 (for uploads) 
 
## Quick Start (Windows and VS Code) 
1. Create and activate virtualenv 
 
```powershell 
python -m venv venv 
venv\Scripts\Activate.ps1 
``` 
 
2. Install dependencies 
 
```powershell 
pip install -r requirements.txt 
pip install -r dev-requirements.txt 
```
 
3. Create `.env` 
- Copy `.env.example` to `.env` and fill values. 
- Minimum required: `DJANGO_SECRET_KEY`, `DATABASE_URL`. 
 
4. Run migrations 
 
```powershell 
python manage.py migrate 
``` 
 
5. Start server 
 
```powershell 
python manage.py runserver 
``` 
 
## Environment Variables (Key Ones) 
 
### Django 
- `DJANGO_SECRET_KEY` (required) 
- `DJANGO_DEBUG` (`True` or `False`) 
- `DJANGO_ALLOWED_HOSTS` (comma separated) 
- `DJANGO_SETTINGS_MODULE` (default `backend.settings.dev`) 
 
### Database 
- `DATABASE_URL` (recommended, example: `postgres://potter:potterpass@localhost:5433/potter_dev`) 
- `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` (fallback) 
 
### Redis 
- `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB` 
 
### S3 or MinIO 
- `AWS_ACCESS_KEY_ID` 
- `AWS_SECRET_ACCESS_KEY` 
- `AWS_STORAGE_BUCKET_NAME` 
- `AWS_S3_REGION_NAME` 
- `AWS_S3_ENDPOINT_URL` 
- `AWS_DEFAULT_ACL` 
 
### Idempotency 
- `IDEMPOTENCY_TTL` (seconds, default 86400) 
 
### Rate Limiting 
- `BOOKINGS_RATE_LIMIT` (default 60) 
- `BOOKINGS_RATE_WINDOW` (seconds, default 3600) 
- `USE_REDIS_CACHE` (True/False) 
- `RATE_LIMIT_FAIL_OPEN` (True/False) 
 
### Auth and JWT 
- `USE_REFRESH_COOKIE` 
- `REFRESH_COOKIE_NAME` 
- `REFRESH_COOKIE_SECURE` 
- `REFRESH_COOKIE_SAMESITE` 
- `REFRESH_COOKIE_PATH` 
- `REFRESH_COOKIE_MAX_AGE` 
- `FRONTEND_PASSWORD_RESET_URL` 
- `PASSWORD_RESET_TIMEOUT` 
 
### Sentry 
- `SENTRY_DSN` (leave empty to disable) 
- `SENTRY_ENVIRONMENT` 
- `SENTRY_TRACES_SAMPLE_RATE` 
- `SENTRY_PROFILES_SAMPLE_RATE` 
- `SENTRY_RELEASE`

### Datadog (Optional Metrics)
- `DATADOG_ENABLED` (`True`/`False`)
- `DATADOG_HOST` (DogStatsD host, default `localhost`)
- `DATADOG_PORT` (DogStatsD port, default `8125`)
- `DATADOG_NAMESPACE` (default `pottershouse`)
- `DATADOG_SERVICE` (default `pottershouse-backend`)
- `DATADOG_ENV` (e.g. `development`, `staging`, `production`)

### Secrets Manager (Optional, AWS)
- `AWS_SECRETS_MANAGER_SECRET_ID` (JSON secret payload)
- `AWS_SECRETS_MANAGER_REQUIRED` (`True` to fail fast if secret fetch fails)
- `AWS_REGION` or `AWS_DEFAULT_REGION`
 
## Migrations 
- Apply migrations: 
 
```powershell 
python manage.py migrate 
``` 
 
- Create new migrations after model changes: 
 
```powershell 
python manage.py makemigrations 
``` 
 
## Testing 
 
### Run bookings tests 
```powershell 
python manage.py test bookings --settings=backend.settings.test 
``` 
 
### Run all tests 
```powershell 
python manage.py test --settings=backend.settings.test 
``` 
 
### Coverage 
```powershell 
pytest --cov=. --cov-report=term-missing 
``` 
 
## Backup and Restore 
- Backup script: `ops/backup.sh` 
- Restore guide: `ops/restore.md`

## Monitoring and Alerts
- Prometheus alert rules: `ops/monitoring/prometheus-alerts.yml`
- Metrics exported via `django-prometheus` and custom app metrics
 
## Health Check 
- `GET /api/v1/health` returns `{'status':'ok','timestamp':'<UTC ISO>'}` 
 
## Notes 
- All timestamps are stored in UTC. 
- Frontend submits Asia/Manila ISO8601 timestamps. 
- Bookings require `Idempotency-Key` header. 
- All errors use the canonical error wrapper.
 
## API Contract (Summary) 
- Base path: /api/v1 
- All responses are JSON 
- Errors use the canonical wrapper with fields: code, message, details 
 
## Required Headers 
- Content-Type: application/json (except multipart) 
- Authorization: Bearer TOKEN (admin endpoints) 
- Idempotency-Key: required for POST /api/v1/bookings 
 
## CORS 
- Allowed origins: https://staging.pottershouse.example.com, https://pottershouse.example.com 
- Allow headers: Content-Type, Authorization, Idempotency-Key 
- Expose headers: Retry-After, Location 
- Allow credentials: true 
 
## Bookings Rules 
- POST /api/v1/bookings auto-confirms when no conflict 
- Conflicts return 409 with canonical wrapper 
- workflow_status drives admin workflow; status is confirmed or cancelled only 
 
## CSV Export 
- GET /api/v1/admin/bookings.csv 
- Columns: id, created_at, customer_name, phone, email, event_type, event_date_start, event_date_end, event_all_day, guests, package_id, dietary_needs, status, workflow_status, deposit_paid, notes 
 
## Background Jobs 
- Email outbox is processed by Celery worker 
- Idempotency cleanup runs daily (task: idempotency_keys.cleanup_idempotency_keys) 
 
## Worker Commands 
- celery -A backend worker -l info 
- celery -A backend beat -l info 
 
## CI 
- GitHub Actions workflow: .github/workflows/ci.yml

## CI/CD (Staging & Production)
- Staging workflow: `.github/workflows/deploy-staging.yml`
- Production workflow: `.github/workflows/deploy-prod.yml`
- Required secrets (for container registry + deploy hook):
  - `REGISTRY_URL`
  - `IMAGE_NAME`
  - `REGISTRY_USERNAME`
  - `REGISTRY_PASSWORD`
  - `STAGING_DEPLOY_WEBHOOK` (optional)
  - `PRODUCTION_DEPLOY_WEBHOOK` (optional)
