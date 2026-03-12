from celery import shared_task
from django.utils import timezone
from .models import IdempotencyKey

@shared_task
def cleanup_idempotency_keys():
    IdempotencyKey.objects.filter(expires_at__lt=timezone.now()).delete()

