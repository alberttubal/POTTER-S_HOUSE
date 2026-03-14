import uuid
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.conf import settings
import sentry_sdk

from core.metrics import inc_http_5xx


class RequestIDMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.request_id = str(uuid.uuid4())

    def process_response(self, request, response):
        if hasattr(request, "request_id"):
            response["X-Request-ID"] = request.request_id
        return response
 
 
class RequireJSONContentTypeMiddleware(MiddlewareMixin): 
    def process_request(self, request): 
        if request.method in ('POST', 'PUT', 'PATCH'): 
            content_type = request.META.get('CONTENT_TYPE', '') 
            if content_type.startswith('multipart/form-data'): 
                return None 
            if not content_type.startswith('application/json'): 
                return JsonResponse( 
                    { 
                        'error': { 
                            'code': 'invalid_content_type', 
                            'message': 'Content-Type must be application/json.', 
                            'details': [], 
                        }, 
                    }, 
                    status=400, 
                ) 
        return None 


class CatchAllExceptionMiddleware(MiddlewareMixin):
    def _is_api_request(self, request):
        return request.path.startswith("/api/")

    def process_exception(self, request, exception):
        if not self._is_api_request(request):
            return None
        sentry_sdk.capture_exception(exception)
        return JsonResponse(
            {
                "error": {
                    "code": "internal_server_error",
                    "message": "An unexpected error occurred",
                    "details": [],
                },
            },
            status=500,
        )

    def process_response(self, request, response):
        if response.status_code >= 500:
            try:
                inc_http_5xx(request.path)
            except Exception:
                pass

        if (
            response.status_code == 404
            and response.get("Content-Type", "").startswith("text/html")
            and self._is_api_request(request)
        ):
            return JsonResponse(
                {
                    "error": {
                        "code": "not_found",
                        "message": "Not Found",
                        "details": [],
                    },
                },
                status=404,
            )
        return response
