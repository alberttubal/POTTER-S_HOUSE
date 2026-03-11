import uuid
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse


class RequestIDMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.request_id = str(uuid.uuid4())

    def process_response(self, request, response):
        if hasattr(request, "request_id"):
            response["X-Request-ID"] = request.request_id
        return response


class CatchAllExceptionMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
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