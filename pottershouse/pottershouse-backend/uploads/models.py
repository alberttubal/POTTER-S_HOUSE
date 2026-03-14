from django.db import models
from core.models import TimeStampedUUIDModel

class Upload(TimeStampedUUIDModel):
    key = models.CharField(max_length=255, unique=True)
    url = models.URLField(max_length=500)
    size = models.BigIntegerField()
    mime_type = models.CharField(max_length=100)
    alt_text = models.CharField(max_length=255, null=True, blank=True)
    published = models.BooleanField(default=False)

    class Meta:
        db_table = "uploads"

    def __str__(self):
        return self.key
