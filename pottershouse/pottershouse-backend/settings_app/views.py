from rest_framework import viewsets

from core.permissions import IsAdminUser
from .models import Setting
from .serializers import SettingSerializer


class SettingAdminViewSet(viewsets.ModelViewSet):
    serializer_class = SettingSerializer
    permission_classes = [IsAdminUser]
    queryset = Setting.objects.all().order_by("key")
