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
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to the Potter's House API! Please refer to the documentation for available endpoints.")

urlpatterns = [
    path("", home),
    path("admin/", admin.site.urls),
    path("api/bookings/", include("bookings.urls")),
    path("api/packages/", include("packages.urls")),
    path("api/admin_users/", include("admin_users.urls")),
    path("api/uploads/", include("uploads.urls")),
    path("api/testimonials/", include("testimonials.urls")),
    path("api/faqs/", include("faqs.urls")),
    path("api/email_outbox/", include("email_outbox.urls")),
    path("api/idempotency_keys/", include("idempotency_keys.urls")),
    path("api/settings/", include("settings_app.urls")),
]