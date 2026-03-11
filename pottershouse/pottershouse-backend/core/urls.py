from django.urls import path
from .views import debug_error

app_name = "core"

urlpatterns = [
    path('debug/error', debug_error),
]