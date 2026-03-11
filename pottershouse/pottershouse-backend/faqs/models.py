from django.db import models
from core.models import TimeStampedUUIDModel

class FAQ(TimeStampedUUIDModel):
    question = models.CharField(max_length=255)
    answer = models.TextField()
    published = models.BooleanField(default=False)

    class Meta:
        db_table = "faqs"

    def __str__(self):
        return self.question
