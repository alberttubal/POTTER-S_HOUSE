from django.urls import path
from .views import SettingPublicList

urlpatterns = [
    path("", SettingPublicList.as_view(), name="settings-public-list"),
]
