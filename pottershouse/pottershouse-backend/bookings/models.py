from django.db import models
from django.core.validators import MinValueValidator
from core.models import TimeStampedUUIDModel
from core.fields import PostgresEnumField
from packages.models import Package

class Booking(TimeStampedUUIDModel):
    STATUS_CHOICES = [
        ("confirmed", "confirmed"),
        ("cancelled", "cancelled"),
    ]
    WORKFLOW_CHOICES = [
        ("new", "new"),
        ("contacted", "contacted"),
        ("confirmed", "confirmed"),
        ("paid", "paid"),
        ("completed", "completed"),
        ("cancelled", "cancelled"),
    ]

    customer_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=40)
    email = models.EmailField()
    event_type = models.CharField(max_length=120)
    event_date_start = models.DateTimeField()
    event_date_end = models.DateTimeField()
    event_all_day = models.BooleanField(default=False)
    guests = models.IntegerField(validators=[MinValueValidator(1)])
    package = models.ForeignKey(
        Package, null=True, blank=True, on_delete=models.SET_NULL, related_name="bookings"
    )
    dietary_needs = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    status = PostgresEnumField(
        enum_name="booking_status",
        max_length=20,
        choices=STATUS_CHOICES,
        default="confirmed",
    )
    workflow_status = PostgresEnumField(
        enum_name="workflow_status",
        max_length=20,
        choices=WORKFLOW_CHOICES,
        default="new",
    )

    deposit_paid = models.BooleanField(default=False)

    class Meta:
        db_table = "bookings"
        indexes = [
            models.Index(fields=["event_date_start"]),
            models.Index(fields=["event_date_end"]),
            models.Index(fields=["workflow_status"]),
        ]

    def __str__(self):
        return f"{self.customer_name} ({self.event_date_start})"
