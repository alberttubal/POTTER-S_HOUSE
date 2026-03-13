from celery import shared_task
from django.db import connection
from core.metrics import set_db_replication_lag


@shared_task
def update_replication_lag():
    lag_seconds = 0.0
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT EXTRACT(EPOCH FROM now() - pg_last_xact_replay_timestamp())'
            )
            row = cursor.fetchone()
        if row and row[0] is not None:
            lag_seconds = float(row[0])
        else:
            lag_seconds = 0.0
    except Exception:
        lag_seconds = 0.0

    set_db_replication_lag(lag_seconds)
    return lag_seconds
