from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .exceptions import canonical_error


def _as_details(data):
    details = []
    if isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and "field" in item and "message" in item:
                details.append({"field": item["field"], "message": str(item["message"])})
            else:
                details.append({"field": None, "message": str(item)})
        return details

    if isinstance(data, dict):
        for field, messages in data.items():
            details.append({"field": field, "message": str(messages)})
        return details

    details.append({"field": None, "message": str(data)})
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
    status_code = response.status_code

    if status_code == 400:
        if isinstance(exc, ValidationError):
            code = "validation_error"
            message = "Validation failed"
        else:
            code = "request_error"
            message = "Request failed"
    elif status_code == 401:
        code = "unauthorized"
        message = "Unauthorized"
    elif status_code == 403:
        code = "forbidden"
        message = "Forbidden"
    elif status_code == 404:
        code = "not_found"
        message = "Not Found"
    elif status_code == 409:
        code = "conflict"
        message = "Conflict"
    elif status_code == 429:
        code = "rate_limited"
        message = "Too many requests"
    else:
        code = "request_error"
        message = "Request failed"

    body, status = canonical_error(
        code,
        message,
        details=details,
        status=status_code,
    )

    response.data = body
    return response
