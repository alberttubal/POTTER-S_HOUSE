from django.urls import path
from .views import BookingCreatePublic

urlpatterns = [
    path("", BookingCreatePublic.as_view(), name="bookings-create"),
]
