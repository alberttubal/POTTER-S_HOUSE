from rest_framework.views import exception_handler
from .exceptions import canonical_error


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        body, status = canonical_error(
            "internal_server_error",
            "An unexpected error occurred",
            status=500,
        )
        from rest_framework.response import Response
        return Response(body, status=status)

    body, status = canonical_error(
        "request_error",
        "Request failed",
        details=response.data,
        status=response.status_code,
    )

    response.data = body
    return response