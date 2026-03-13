from rest_framework.routers import DefaultRouter
from .views import FAQAdminViewSet

router = DefaultRouter()
router.register(r"", FAQAdminViewSet, basename="admin-faqs")

urlpatterns = router.urls
