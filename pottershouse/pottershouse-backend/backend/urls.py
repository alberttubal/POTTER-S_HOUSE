from django.contrib import admin
from django.urls import path, include, re_path
from django.http import JsonResponse
from django.utils import timezone

from admin_users.views import AdminLoginView, AdminRefreshView, AdminPasswordForgotView, AdminPasswordResetView

def home(request):
    return JsonResponse({'message': "Welcome to Potter's House API. See /api/v1/health"})

def health(request):
    return JsonResponse(
        {'status': 'ok', 'timestamp': timezone.now().isoformat()}
    )

def _json_error(code, message):
    return JsonResponse({'error': {'code': code, 'message': message, 'details': []}})

def custom_404(request, exception):
    return _json_error('not_found', 'Not Found')

def custom_500(request):
    return _json_error('internal_server_error', 'An internal server error occurred.')

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    re_path(r'^api/v1/health/?$', health, name='api-health'),

    re_path(r'^api/v1/admin/login/?$', AdminLoginView.as_view()),
    re_path(r'^api/v1/admin/refresh/?$', AdminRefreshView.as_view()),
    re_path(r'^api/v1/admin/password/forgot/?$', AdminPasswordForgotView.as_view()),
    re_path(r'^api/v1/admin/password/reset/?$', AdminPasswordResetView.as_view()),

    re_path(r'^api/v1/bookings/?', include('bookings.urls')),
    re_path(r'^api/v1/packages/?', include('packages.urls')),
    re_path(r'^api/v1/admin/packages/?', include('packages.admin_urls')),
    re_path(r'^api/v1/admin/bookings/?', include('bookings.admin_urls')),
    re_path(r'^api/v1/admin/uploads/?', include('uploads.admin_urls')),
    re_path(r'^api/v1/admin_users/?', include('admin_users.urls')),
    re_path(r'^api/v1/gallery/?', include('uploads.urls')),
    re_path(r'^api/v1/testimonials/?', include('testimonials.urls')),
    re_path(r'^api/v1/faqs/?', include('faqs.urls')),
    re_path(r'^api/v1/email_outbox/?', include('email_outbox.urls')),
    re_path(r'^api/v1/idempotency_keys/?', include('idempotency_keys.urls')),
    re_path(r'^api/v1/settings/?', include('settings_app.urls')),
    re_path(r'^api/v1/core/?', include('core.urls')),
]

handler404 = 'backend.urls.custom_404'
handler500 = 'backend.urls.custom_500'
