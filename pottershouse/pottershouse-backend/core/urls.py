from django.conf import settings
from django.urls import path
from .views import debug_error

app_name = "core"

urlpatterns = []

if settings.DEBUG:
    urlpatterns += [
        path("debug/error", debug_error),
    ]
