from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Package
from .serializers import PackageSerializer

class PackageListPublic(generics.ListAPIView):
    serializer_class = PackageSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = Package.objects.all().order_by("name")
        active = self.request.query_params.get("active")
        if active is not None:
            if active.lower() == "true":
                qs = qs.filter(active=True)
            elif active.lower() == "false":
                qs = qs.filter(active=False)
        return qs

class PackageDetailPublic(generics.RetrieveAPIView):
    serializer_class = PackageSerializer
    permission_classes = [AllowAny]
    queryset = Package.objects.all()

class PackageAdminViewSet(viewsets.ModelViewSet):
    serializer_class = PackageSerializer
    permission_classes = [IsAuthenticated]
    queryset = Package.objects.all()
