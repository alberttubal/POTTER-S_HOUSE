from prometheus_client import Counter, Gauge

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

DB_REPLICATION_LAG_SECONDS = Gauge(
    "pottershouse_db_replication_lag_seconds",
    "Database replication lag in seconds (0 if not applicable)",
)


def inc_bookings_created():
    BOOKINGS_CREATED_TOTAL.inc()


def observe_outbox_latency(seconds):
    if seconds is None:
        return
    OUTBOX_QUEUE_LATENCY_SECONDS.set(max(float(seconds), 0.0))


def set_db_replication_lag(seconds):
    if seconds is None:
        seconds = 0.0
    DB_REPLICATION_LAG_SECONDS.set(max(float(seconds), 0.0))
