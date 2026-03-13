from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny

from core.permissions import IsAdminUser
from .models import Testimonial
from .serializers import TestimonialSerializer


class TestimonialPublicList(generics.ListAPIView):
    serializer_class = TestimonialSerializer
    permission_classes = [AllowAny]
    queryset = Testimonial.objects.filter(published=True).order_by("-created_at")


class TestimonialAdminViewSet(viewsets.ModelViewSet):
    serializer_class = TestimonialSerializer
    permission_classes = [IsAdminUser]
    queryset = Testimonial.objects.all().order_by("-created_at")
