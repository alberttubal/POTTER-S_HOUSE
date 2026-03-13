from django.urls import path
from .views import TestimonialPublicList

app_name = "testimonials"

urlpatterns = [
    path("", TestimonialPublicList.as_view(), name="testimonials-public"),
]
