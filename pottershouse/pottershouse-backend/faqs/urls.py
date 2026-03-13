from django.urls import path
from .views import FAQPublicList

app_name = "faqs"

urlpatterns = [
    path("", FAQPublicList.as_view(), name="faqs-public"),
]
