from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny

from core.permissions import IsAdminUser, RBACPermission
from .models import Testimonial
from .serializers import TestimonialSerializer


class TestimonialPublicList(generics.ListAPIView):
    serializer_class = TestimonialSerializer
    permission_classes = [AllowAny]
    queryset = Testimonial.objects.filter(published=True).order_by("-created_at")


class TestimonialAdminViewSet(viewsets.ModelViewSet):
    serializer_class = TestimonialSerializer
    permission_classes = [IsAdminUser, RBACPermission]
    permission_map = {"GET": "testimonials.view_testimonial", "POST": "testimonials.add_testimonial", "PUT": "testimonials.change_testimonial", "PATCH": "testimonials.change_testimonial", "DELETE": "testimonials.delete_testimonial"}
    queryset = Testimonial.objects.all().order_by("-created_at")
