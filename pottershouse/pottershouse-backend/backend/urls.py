"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""


# backend/urls.py
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.utils import timezone

def home(request):
    return JsonResponse({"message": "Welcome to Potter's House API. See /api/v1/health"}, status=200)

def health(request):
    # Return UTC timestamp (Django USE_TZ=True ensures timezone.now() is UTC)
    return JsonResponse({
        "status": "ok",
        "timestamp": timezone.now().isoformat()
    })

def _json_error(code, message):
    return JsonResponse({"error": {"code": code, "message": message, "details": []}})

def custom_404(request, exception):
    return _json_error("not_found", "Not Found")

def custom_500(request):
    return _json_error("internal_server_error", "An internal server error occurred.")



urlpatterns = [
    path("", home),
    path("admin/", admin.site.urls),
    # Public API (versioned)
    path("api/v1/health/", health, name="api-health"),
    path("api/v1/bookings/", include("bookings.urls")),
    path("api/v1/packages/", include("packages.urls")),
    path("api/v1/admin_users/", include("admin_users.urls")),
    path("api/v1/uploads/", include("uploads.urls")),
    path("api/v1/testimonials/", include("testimonials.urls")),
    path("api/v1/faqs/", include("faqs.urls")),
    path("api/v1/email_outbox/", include("email_outbox.urls")),
    path("api/v1/idempotency_keys/", include("idempotency_keys.urls")),
    path("api/v1/settings/", include("settings_app.urls")),
    path('api/v1/core/', include('core.urls')),
]

handler404 = "backend.urls.custom_404"
handler500 = "backend.urls.custom_500"
