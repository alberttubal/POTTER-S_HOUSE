import time
import logging

from django.conf import settings
from django.core.cache import cache

from core.utils import error_response

logger = logging.getLogger(__name__)


def rate_limit(key_prefix, limit, window_seconds):
    def decorator(view_func):
        def _wrapped(*args, **kwargs):
            # Supports both function-based and method-based views.
            request = args[0] if len(args) == 1 else args[1]
            forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
            ip = (
                forwarded.split(',')[0].strip()
                if forwarded
                else request.META.get('REMOTE_ADDR', 'unknown')
            )

            key = '{}:{}'.format(key_prefix, ip)
            now = int(time.time())

            try:
                current = cache.get(key)

                if not current:
                    cache.set(key, (1, now), timeout=window_seconds)
                else:
                    count, start = current
                    if now - start < window_seconds:
                        if count >= limit:
                            retry_after = window_seconds - (now - start)
                            response = error_response(
                                code='rate_limited',
                                message='Too many requests',
                                details=[],
                                status=429,
                            )
                            response['Retry-After'] = str(retry_after)
                            return response
                        cache.set(key, (count + 1, start), timeout=window_seconds)
                    else:
                        cache.set(key, (1, now), timeout=window_seconds)
            except Exception as exc:
                if getattr(settings, "RATE_LIMIT_FAIL_OPEN", True):
                    logger.warning("Rate limit cache error, allowing request.", exc_info=exc)
                    return view_func(*args, **kwargs)
                return error_response(
                    code="rate_limit_unavailable",
                    message="Rate limiting is temporarily unavailable.",
                    details=[],
                    status=500,
                )

            return view_func(*args, **kwargs)

        return _wrapped

    return decorator
