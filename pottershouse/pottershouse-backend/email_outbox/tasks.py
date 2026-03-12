from celery import shared_task
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from .models import EmailOutbox

@shared_task(bind=True, max_retries=5, default_retry_delay=30)
def process_email_outbox(self, outbox_id):
    try:
        msg = EmailOutbox.objects.get(id=outbox_id, status="queued")
    except EmailOutbox.DoesNotExist:
        return

    try:
        send_mail(
            subject=msg.subject,
            message=msg.payload.get("body", ""),
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@pottershouse.com"),
            recipient_list=[msg.to_email],
            fail_silently=False,
        )
        msg.status = "sent"
        msg.sent_at = timezone.now()
        msg.save(update_fields=["status", "sent_at"])
    except Exception:
        msg.attempts += 1
        msg.last_attempt_at = timezone.now()
        msg.status = "failed" if msg.attempts >= 5 else "queued"
        msg.save(update_fields=["attempts", "last_attempt_at", "status"])
        raise self.retry()
