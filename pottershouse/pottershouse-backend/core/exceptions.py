def canonical_error(code, message, details=None, status=400, **extra):
    """
    Build canonical error wrapper required by the API contract.
    """
    body = {
        "error": {
            "code": code,
            "message": message,
            "details": details or [],
        }
    }

    if extra:
        body["error"].update(extra)

    return body, status