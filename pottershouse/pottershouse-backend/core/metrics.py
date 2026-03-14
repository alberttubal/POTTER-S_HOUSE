from prometheus_client import Counter, Gauge

from core.datadog import get_default_tags, get_statsd

BOOKINGS_CREATED_TOTAL = Counter(
    "pottershouse_bookings_created_total",
    "Total number of bookings created",
)

HTTP_5XX_TOTAL = Counter(
    "pottershouse_http_5xx_total",
    "Total number of 5xx responses",
    ["path"],
)

OUTBOX_QUEUE_LATENCY_SECONDS = Gauge(
    "pottershouse_outbox_queue_latency_seconds",
    "Queue latency in seconds for email outbox messages",
)

OUTBOX_BACKLOG_TOTAL = Gauge(
    "pottershouse_outbox_backlog_total",
    "Total number of queued/failed email outbox messages",
)

DB_REPLICATION_LAG_SECONDS = Gauge(
    "pottershouse_db_replication_lag_seconds",
    "Database replication lag in seconds (0 if not applicable)",
)


def inc_bookings_created():
    BOOKINGS_CREATED_TOTAL.inc()
    statsd = get_statsd()
    if statsd:
        statsd.increment("bookings.created", tags=get_default_tags())


def inc_http_5xx(path):
    try:
        HTTP_5XX_TOTAL.labels(path=path).inc()
    except Exception:
        pass
    statsd = get_statsd()
    if statsd:
        statsd.increment("http.5xx", tags=get_default_tags([f"path:{path}"]))


def observe_outbox_latency(seconds):
    if seconds is None:
        return
    value = max(float(seconds), 0.0)
    OUTBOX_QUEUE_LATENCY_SECONDS.set(value)
    statsd = get_statsd()
    if statsd:
        statsd.gauge("outbox.queue_latency_seconds", value, tags=get_default_tags())


def set_outbox_backlog(count):
    value = max(int(count), 0)
    OUTBOX_BACKLOG_TOTAL.set(value)
    statsd = get_statsd()
    if statsd:
        statsd.gauge("outbox.backlog_total", value, tags=get_default_tags())


def set_db_replication_lag(seconds):
    if seconds is None:
        seconds = 0.0
    value = max(float(seconds), 0.0)
    DB_REPLICATION_LAG_SECONDS.set(value)
    statsd = get_statsd()
    if statsd:
        statsd.gauge("db.replication_lag_seconds", value, tags=get_default_tags())
