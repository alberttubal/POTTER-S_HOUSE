from django.urls import path
from .views import PackageListPublic, PackageDetailPublic

urlpatterns = [
    path("", PackageListPublic.as_view(), name="packages-list"),
    path("<uuid:pk>/", PackageDetailPublic.as_view(), name="packages-detail"),
]
