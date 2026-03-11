from rest_framework import serializers
from .models import Package

class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = [
            "id", "name", "description", "price", "active",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
