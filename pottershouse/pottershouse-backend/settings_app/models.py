from django.db import models
from core.models import TimeStampedUUIDModel

class Setting(TimeStampedUUIDModel):
    key = models.CharField(max_length=100, unique=True)
    value = models.JSONField()

    class Meta:
        db_table = "settings"

    def __str__(self):
        return self.key
