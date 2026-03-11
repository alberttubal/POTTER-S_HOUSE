from rest_framework import serializers
from .models import AdminUser

class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminUser
        fields = ["id", "email", "full_name", "is_staff", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
