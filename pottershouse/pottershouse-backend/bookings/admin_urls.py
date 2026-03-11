from django.urls import path
from .views import BookingAdminList, BookingAdminDetail

urlpatterns = [
    path("", BookingAdminList.as_view(), name="admin-bookings-list"),
    path("<uuid:pk>/", BookingAdminDetail.as_view(), name="admin-bookings-detail"),
]
