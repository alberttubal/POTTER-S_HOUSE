from django.core.management.base import BaseCommand
from django.utils import timezone
from idempotency_keys.models import IdempotencyKey

class Command(BaseCommand):
    help = "Delete expired idempotency keys"

    def handle(self, *args, **options):
        deleted, _ = IdempotencyKey.objects.filter(expires_at__lt=timezone.now()).delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} expired idempotency keys"))
