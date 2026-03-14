from django.urls import path
from .views import UploadCreateAdmin, UploadAdminList, UploadAdminDetail, UploadPresignAdmin

urlpatterns = [
    path("", UploadCreateAdmin.as_view(), name="admin-uploads"),
    path("presign/", UploadPresignAdmin.as_view(), name="admin-uploads-presign"),
    path("list/", UploadAdminList.as_view(), name="admin-uploads-list"),
    path("<uuid:pk>/", UploadAdminDetail.as_view(), name="admin-uploads-detail"),
]
