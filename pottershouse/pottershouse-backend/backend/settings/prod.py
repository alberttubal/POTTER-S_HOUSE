
from .base import *

DEBUG = False
# In production, DJANGO_ALLOWED_HOSTS must be set in .env
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",")
