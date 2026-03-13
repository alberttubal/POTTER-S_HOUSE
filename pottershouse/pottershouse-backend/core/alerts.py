import logging
import os
import requests

logger = logging.getLogger(__name__)


def send_pagerduty_event(summary, severity='error', source='pottershouse-backend', custom_details=None):
    routing_key = os.getenv('PAGERDUTY_ROUTING_KEY', '').strip()
    if not routing_key:
        return False

    payload = {
        'routing_key': routing_key,
        'event_action': 'trigger',
        'payload': {
            'summary': summary,
            'source': source,
            'severity': severity,
        },
    }

    if custom_details:
        payload['payload']['custom_details'] = custom_details

    try:
        response = requests.post(
            'https://events.pagerduty.com/v2/enqueue',
            json=payload,
            timeout=5,
        )
        if response.status_code >= 300:
            logger.warning('PagerDuty event failed: %s', response.text)
            return False
    except Exception as exc:
        logger.warning('PagerDuty event error: %s', exc)
        return False
    return True
