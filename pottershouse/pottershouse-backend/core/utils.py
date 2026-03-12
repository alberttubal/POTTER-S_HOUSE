from rest_framework.response import Response
import hashlib
import json

def request_hash(data):
    raw = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

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
