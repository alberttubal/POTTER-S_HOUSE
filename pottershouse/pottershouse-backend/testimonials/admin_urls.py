from rest_framework.routers import DefaultRouter
from .views import TestimonialAdminViewSet

router = DefaultRouter()
router.register(r"", TestimonialAdminViewSet, basename="admin-testimonials")

urlpatterns = router.urls
