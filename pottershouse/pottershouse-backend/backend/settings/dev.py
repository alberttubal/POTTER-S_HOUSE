from .base import *
import os

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = "no-reply@pottershouse.com"

BOOKINGS_RATE_LIMIT = int(os.getenv("BOOKINGS_RATE_LIMIT", "60"))
BOOKINGS_RATE_WINDOW = int(os.getenv("BOOKINGS_RATE_WINDOW", "3600"))
RATE_LIMIT_FAIL_OPEN = os.getenv("RATE_LIMIT_FAIL_OPEN", "True") == "True"
USE_REDIS_CACHE = os.getenv("USE_REDIS_CACHE", "False") == "True"

if USE_REDIS_CACHE:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": f"redis://{os.getenv('REDIS_HOST','localhost')}:{os.getenv('REDIS_PORT','6379')}/{os.getenv('REDIS_DB','1')}",
            "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "pottershouse-dev",
        }
    }
