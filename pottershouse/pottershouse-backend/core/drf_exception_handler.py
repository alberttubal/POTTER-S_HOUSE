from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .exceptions import canonical_error

def _as_details(data):
    details = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and "field" in item and "message" in item:
                details.append(item)
            else:
                details.append({"field": None, "message": item})
        return details

    if isinstance(data, dict):
        for field, messages in data.items():
            details.append({"field": field, "message": messages})
        return details

    details.append({"field": None, "message": data})
    return details

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        body, status = canonical_error(
            "internal_server_error",
            "An unexpected error occurred",
            status=500,
        )
        return Response(body, status=status)

    details = _as_details(response.data)
    if isinstance(exc, ValidationError) or response.status_code == 400:
        code = "validation_error"
        message = "Validation failed"
    else:
        code = "request_error"
        message = "Request failed"

    body, status = canonical_error(
        code,
        message,
        details=details,
        status=response.status_code,
    )

    response.data = body
    return response
