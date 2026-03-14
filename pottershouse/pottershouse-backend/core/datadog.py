import logging
import os

logger = logging.getLogger(__name__)

_statsd_client = None
_initialized = False


def _bool_env(name, default="False"):
    return os.getenv(name, default).strip().lower() == "true"


def get_default_tags(extra=None):
    tags = []
    service = os.getenv("DATADOG_SERVICE")
    env = os.getenv("DATADOG_ENV")
    if service:
        tags.append("service:{}".format(service))
    if env:
        tags.append("env:{}".format(env))
    if extra:
        tags.extend(extra)
    return tags


def get_statsd():
    global _statsd_client, _initialized
    if _initialized:
        return _statsd_client

    _initialized = True
    if not _bool_env("DATADOG_ENABLED", "False"):
        return None

    try:
        from datadog import initialize, statsd
    except Exception as exc:
        logger.warning("Datadog client unavailable: %s", exc)
        return None

    host = os.getenv("DATADOG_HOST", "localhost")
    port = int(os.getenv("DATADOG_PORT", "8125"))
    namespace = os.getenv("DATADOG_NAMESPACE", "pottershouse")

    initialize(statsd_host=host, statsd_port=port, namespace=namespace)
    _statsd_client = statsd
    return _statsd_client
