from django.db import models
from core.models import TimeStampedUUIDModel

class EmailOutbox(TimeStampedUUIDModel):
    STATUS_CHOICES = [
        ("queued", "queued"),
        ("sent", "sent"),
        ("failed", "failed"),
    ]

    to_email = models.EmailField()
    subject = models.CharField(max_length=255)
    template = models.CharField(max_length=120)
    payload = models.JSONField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="queued")
    attempts = models.PositiveIntegerField(default=0)
    last_attempt_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "email_outbox"

    def __str__(self):
        return f"{self.to_email} ({self.status})"
    
    @classmethod
    def queue_booking_email(cls, booking):
        return cls.objects.create(
            to_email=booking.email,
            subject="Booking received",
            template="booking_received",
            payload={"booking_id": str(booking.id), "customer_name": booking.customer_name},
        )

