## Monitoring and Alerts

This project exports Prometheus metrics via `django-prometheus`.

### Alert Rules
- Prometheus alert rules live in `ops/monitoring/prometheus-alerts.yml`.
- Load these rules into your Prometheus server or Alertmanager stack.

### Key Metrics
- `django_http_responses_total_by_status_total` (provided by django-prometheus)
- `pottershouse_outbox_backlog_total`
- `pottershouse_outbox_queue_latency_seconds`
- `pottershouse_http_5xx_total`
