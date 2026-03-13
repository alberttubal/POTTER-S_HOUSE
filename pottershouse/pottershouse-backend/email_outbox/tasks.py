from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone
import sentry_sdk

from .models import EmailOutbox, MAX_RETRY_ATTEMPTS, ALERT_AFTER_ATTEMPTS


def _render_body(template_name, payload):
    template_path = 'emails/{}.txt'.format(template_name)
    return render_to_string(template_path, payload)


def _send_message(message):
    now = timezone.now()
    try:
        payload = dict(message.payload or {})
        payload.setdefault(
            'whatsapp_link',
            getattr(settings, 'WHATSAPP_CONTACT_LINK', 'https://wa.me/639171234567?text=Hello')
        )
        body = _render_body(message.template, payload)
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@pottershouse.com')
        send_mail(
            message.subject,
            body,
            from_email,
            [message.to_email],
            fail_silently=False,
        )
    except Exception as exc:
        message.mark_failed(str(exc))
        if message.attempts > ALERT_AFTER_ATTEMPTS:
            message.manual_review = True
            message.save(update_fields=['manual_review', 'updated_at'])
            with sentry_sdk.push_scope() as scope:
                scope.set_context('email_outbox', {
                    'email_outbox_id': str(message.id),
                    'to_email': message.to_email,
                    'attempts': message.attempts,
                })
                sentry_sdk.capture_message(
                    'Email outbox failed more than 3 times (manual review required)',
                    level='error'
                )
        return False

    message.mark_sent()
    message.last_attempt_at = now
    message.save(update_fields=['last_attempt_at', 'updated_at'])
    return True


@shared_task
def process_email_outbox(limit=50):
    with transaction.atomic():
        candidates = list(
            EmailOutbox.objects.select_for_update(skip_locked=True)
            .filter(status__in=['queued', 'failed'])
            .order_by('created_at')[:limit]
        )

        messages = []
        for message in candidates:
            if message.status == 'failed' and not message.should_retry():
                continue
            message.status = 'processing'
            message.save(update_fields=['status', 'updated_at'])
            messages.append(message)

    for message in messages:
        if message.attempts >= MAX_RETRY_ATTEMPTS and message.status != 'processing':
            continue
        _send_message(message)


@shared_task
def dispatch_outbox():
    process_email_outbox.delay()
