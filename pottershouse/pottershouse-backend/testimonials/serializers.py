from rest_framework import serializers
from .models import Testimonial

class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = [
            "id", "customer_name", "content", "published",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
