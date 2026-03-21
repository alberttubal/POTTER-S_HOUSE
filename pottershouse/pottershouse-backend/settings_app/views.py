from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny

from core.permissions import IsAdminUser, RBACPermission
from .models import Setting
from .serializers import SettingSerializer

PUBLIC_SETTING_KEYS = {
    "contact_phone",
    "contact_phone_primary",
    "contact_phone_secondary",
    "business_address",
    "facebook_url",
    "whatsapp_number",
    "contact_email",
}


class SettingPublicList(generics.ListAPIView):
    serializer_class = SettingSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Setting.objects.filter(key__in=PUBLIC_SETTING_KEYS).order_by("key")


class SettingAdminViewSet(viewsets.ModelViewSet):
    serializer_class = SettingSerializer
    permission_classes = [IsAdminUser, RBACPermission]
    permission_map = {
        "GET": "settings_app.view_setting",
        "POST": "settings_app.add_setting",
        "PUT": "settings_app.change_setting",
        "PATCH": "settings_app.change_setting",
        "DELETE": "settings_app.delete_setting",
    }
    queryset = Setting.objects.all().order_by("key")
