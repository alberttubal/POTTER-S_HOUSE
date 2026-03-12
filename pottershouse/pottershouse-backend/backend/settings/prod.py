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

DEBUG = False
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",")
