from django.utils import timezone
from rest_framework import serializers
from .models import Booking

class BookingSerializer(serializers.ModelSerializer):
    honeypot = serializers.CharField(write_only=True, required=True, allow_blank=True)

    class Meta:
        model = Booking
        fields = [
            "id", "customer_name", "phone", "email", "event_type",
            "event_date_start", "event_date_end", "event_all_day",
            "guests", "package", "dietary_needs", "notes",
            "status", "workflow_status", "deposit_paid",
            "created_at", "updated_at",
            "honeypot",
        ]
        read_only_fields = ["id", "status", "workflow_status", "created_at", "updated_at"]

    def validate_honeypot(self, value):
        if value:
            raise serializers.ValidationError("Honeypot field must be empty.")
        return value

    def create(self, validated_data):
        validated_data.pop("honeypot", None)
        return super().create(validated_data)

    def validate(self, attrs):
        now = timezone.now()
        if attrs["event_date_start"] < now:
            raise serializers.ValidationError({
                "event_date_start": "event_date_start cannot be in the past." 
            })
        if attrs["event_date_end"] < attrs["event_date_start"]:
            raise serializers.ValidationError({
                "event_date_end": "event_date_end must be after or equal to event_date_start." 
            })
        return attrs
