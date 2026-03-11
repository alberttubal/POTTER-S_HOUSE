from rest_framework.response import Response

def error_response(code, message, details=None, status=400, **extra):
    payload = {
        "error": {
            "code": code,
            "message": message,
            "details": details or [],
        }
    }
    for key, value in extra.items():
        payload["error"][key] = value
    return Response(payload, status=status)
