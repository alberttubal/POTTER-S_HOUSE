from django.urls import path


def test_error(request):
    raise Exception("Test error")


urlpatterns = [
    path("api/v1/test-error", test_error),
]
