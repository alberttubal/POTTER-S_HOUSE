from django.db import models
from core.models import TimeStampedUUIDModel

class Package(TimeStampedUUIDModel):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "packages"

    def __str__(self):
        return self.name
