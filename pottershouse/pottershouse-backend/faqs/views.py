from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny

from core.permissions import IsAdminUser, RBACPermission
from .models import FAQ
from .serializers import FAQSerializer


class FAQPublicList(generics.ListAPIView):
    serializer_class = FAQSerializer
    permission_classes = [AllowAny]
    queryset = FAQ.objects.filter(published=True).order_by("-created_at")


class FAQAdminViewSet(viewsets.ModelViewSet):
    serializer_class = FAQSerializer
    permission_classes = [IsAdminUser, RBACPermission]
    permission_map = {"GET": "faqs.view_faq", "POST": "faqs.add_faq", "PUT": "faqs.change_faq", "PATCH": "faqs.change_faq", "DELETE": "faqs.delete_faq"}
    queryset = FAQ.objects.all().order_by("-created_at")
