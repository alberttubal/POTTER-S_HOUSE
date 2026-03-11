from django.db import models
from core.models import TimeStampedUUIDModel

class Testimonial(TimeStampedUUIDModel):
    customer_name = models.CharField(max_length=150)
    content = models.TextField()
    published = models.BooleanField(default=False)

    class Meta:
        db_table = "testimonials"

    def __str__(self):
        return self.customer_name
