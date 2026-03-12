import uuid
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.conf import settings
import sentry_sdk



class RequestIDMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.request_id = str(uuid.uuid4())

    def process_response(self, request, response):
        if hasattr(request, "request_id"):
            response["X-Request-ID"] = request.request_id
        return response


class CatchAllExceptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            return self.get_response(request)
        except Exception as e:
            if settings.DEBUG:
                raise 
            sentry_sdk.capture_exception(e)
            return JsonResponse(
                {
                    "error": {
                        "code": "internal_server_error",
                        "message": "An unexpected error occurred",
                        "details": [],
                    }
                },
                status=500,
            )

    def process_response(self, request, response):
        """
        Convert Django HTML 404 responses into canonical JSON errors.
        Needed because DEBUG=True bypasses handler404.
        """
        if response.status_code == 404 and response.get("Content-Type", "").startswith("text/html"):
            return JsonResponse(
                {
                    "error": {
                        "code": "not_found",
                        "message": "Not Found",
                        "details": [],
                    }
                },
                status=404,
            )
        return response