from .base import *
import os

BOOKINGS_RATE_LIMIT = int(os.getenv("BOOKINGS_RATE_LIMIT", "60"))
BOOKINGS_RATE_WINDOW = int(os.getenv("BOOKINGS_RATE_WINDOW", "3600"))
RATE_LIMIT_FAIL_OPEN = os.getenv("RATE_LIMIT_FAIL_OPEN", "False") == "True"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT','6379')}/{os.getenv('REDIS_DB','1')}",
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}

REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
redis_url = f"redis://{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT','6379')}/{os.getenv('REDIS_DB','1')}"
if REDIS_PASSWORD:
    redis_url = f"redis://:{REDIS_PASSWORD}@{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT','6379')}/{os.getenv('REDIS_DB','1')}"
CACHES["default"]["LOCATION"] = redis_url

DEBUG = False
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost").split(",")

# TLS / Security headers
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Logging for production
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "root": {"handlers": ["console"], "level": os.getenv("LOG_LEVEL", "INFO")},
}

# Static/Media files (important for Docker)
STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Sentry error tracking (you have it in .env)
if os.getenv("SENTRY_DSN"):
    import sentry_sdk
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        environment=os.getenv("SENTRY_ENVIRONMENT", "production"),
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.0")),
    )
