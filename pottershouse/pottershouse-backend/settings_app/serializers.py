from rest_framework import serializers
from .models import Setting

class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setting
        fields = ["id", "key", "value", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
