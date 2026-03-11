from rest_framework.routers import DefaultRouter
from .views import PackageAdminViewSet

router = DefaultRouter()
router.register(r"", PackageAdminViewSet, basename="admin-packages")

urlpatterns = router.urls
