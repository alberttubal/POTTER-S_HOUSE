from django.db import models
from django.utils import timezone
from datetime import timedelta
import os

    
class IdempotencyKey(models.Model):
    key = models.CharField(max_length=255, primary_key=True)
    request_hash = models.CharField(max_length=64)
    response_status = models.IntegerField(null=True, blank=True)
    response_headers = models.JSONField(null=True, blank=True)
    response_body = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def ttl_expires_at(cls):
        return timezone.now() + timedelta(seconds=int(os.getenv("IDEMPOTENCY_TTL", "86400")))

    class Meta:
        db_table = "idempotency_keys"
        indexes = [
            models.Index(fields=["expires_at"], name="idx_idempotency_expires_at"),
        ]

    def __str__(self):
        return self.key
