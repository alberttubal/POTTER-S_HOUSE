from django.http import JsonResponse
from django.utils.timezone import now


def health(request):
    return JsonResponse(
        {
            "status": "ok",
            "timestamp": now().isoformat(),
        }
    )


def debug_error(request):
    raise Exception("Test error for Sentry")