from datetime import timedelta
from django.db import models
from django.utils import timezone
from core.models import TimeStampedUUIDModel

MAX_RETRY_ATTEMPTS = 5
RETRY_INITIAL_DELAY = 30
RETRY_MULTIPLIER = 2
ALERT_AFTER_ATTEMPTS = 3


class EmailOutboxManager(models.Manager):
    def pending(self):
        return self.filter(status__in=["queued", "processing"])

    def failed(self):
        return self.filter(status="failed")

    def needs_retry(self):
        return self.filter(status="failed", attempts__lt=MAX_RETRY_ATTEMPTS)


class EmailOutbox(TimeStampedUUIDModel):
    STATUS_CHOICES = [
        ("queued", "queued"),
        ("processing", "processing"),
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
    error_message = models.TextField(null=True, blank=True)
    manual_review = models.BooleanField(default=False)

    objects = EmailOutboxManager()

    class Meta:
        db_table = "email_outbox"
        indexes = [
            models.Index(fields=["status", "created_at"]),
            models.Index(fields=["to_email"]),
            models.Index(fields=["sent_at"]),
        ]

    def __str__(self):
        return f"{self.to_email} ({self.status})"

    def __repr__(self):
        return f"<EmailOutbox({self.to_email}, {self.status}, attempts={self.attempts})>"

    def should_retry(self):
        if self.status != "failed" or self.attempts >= MAX_RETRY_ATTEMPTS:
            return False
        if not self.last_attempt_at:
            return True
        delay = RETRY_INITIAL_DELAY * (RETRY_MULTIPLIER ** max(self.attempts - 1, 0))
        return timezone.now() >= self.last_attempt_at + timedelta(seconds=delay)

    def mark_sent(self):
        self.status = "sent"
        self.sent_at = timezone.now()
        self.save(update_fields=["status", "sent_at", "updated_at"])

    def mark_failed(self, error_msg):
        self.status = "failed"
        self.error_message = error_msg
        self.attempts += 1
        self.last_attempt_at = timezone.now()
        if self.attempts > ALERT_AFTER_ATTEMPTS:
            self.manual_review = True
        self.save(update_fields=["status", "error_message", "attempts", "last_attempt_at", "manual_review", "updated_at"])

    @classmethod
    def queue_booking_email(cls, booking):
        return cls.objects.create(
            to_email=booking.email,
            subject="Booking received",
            template="booking_received",
            payload={
                "booking_id": str(booking.id),
                "customer_name": booking.customer_name,
                "event_date": booking.event_date_start.isoformat(),
                "package_name": booking.package.name if booking.package else "N/A",
            },
        )
