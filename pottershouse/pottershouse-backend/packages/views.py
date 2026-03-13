from django.core.cache import cache
from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.pagination import StandardResultsSetPagination
from core.permissions import IsAdminUser
from .models import Package
from .serializers import PackageSerializer

class PackageListPublic(generics.ListAPIView):
    serializer_class = PackageSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = Package.objects.all().order_by("name")
        active = self.request.query_params.get("active")
        if active is not None:
            if active.lower() == "true":
                qs = qs.filter(active=True)
            elif active.lower() == "false":
                qs = qs.filter(active=False)
        return qs

    def list(self, request, *args, **kwargs):
        active = request.query_params.get("active")
        page = request.query_params.get("page", "1")
        page_size = request.query_params.get("pageSize") or str(self.pagination_class.page_size)
        cache_key = f"packages:active={active}:page={page}:pageSize={page_size}"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=60)
        return response

class PackageDetailPublic(generics.RetrieveAPIView):
    serializer_class = PackageSerializer
    permission_classes = [AllowAny]
    queryset = Package.objects.all()

class PackageAdminViewSet(viewsets.ModelViewSet):
    serializer_class = PackageSerializer
    permission_classes = [IsAdminUser]
    queryset = Package.objects.all()
