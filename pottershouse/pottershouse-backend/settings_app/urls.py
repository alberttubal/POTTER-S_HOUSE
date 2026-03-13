from rest_framework.routers import DefaultRouter
from .views import SettingAdminViewSet

router = DefaultRouter()
router.register(r"", SettingAdminViewSet, basename="admin-settings")

urlpatterns = router.urls
