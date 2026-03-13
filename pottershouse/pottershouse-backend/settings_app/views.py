from rest_framework import viewsets

from core.permissions import IsAdminUser, RBACPermission
from .models import Setting
from .serializers import SettingSerializer


class SettingAdminViewSet(viewsets.ModelViewSet):
    serializer_class = SettingSerializer
    permission_classes = [IsAdminUser, RBACPermission]
    permission_map = {"GET": "settings_app.view_setting", "POST": "settings_app.add_setting", "PUT": "settings_app.change_setting", "PATCH": "settings_app.change_setting", "DELETE": "settings_app.delete_setting"}
    queryset = Setting.objects.all().order_by("key")
