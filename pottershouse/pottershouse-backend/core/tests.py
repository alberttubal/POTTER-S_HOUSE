from django.test import TestCase, override_settings
from rest_framework.test import APIClient


class JsonErrorResponseTests(TestCase):
    @override_settings(DEBUG=True, ROOT_URLCONF="core.tests_urls")
    def test_api_exception_returns_json_in_debug(self):
        client = APIClient()
        client.raise_request_exception = False
        response = client.get("/api/v1/test-error")
        self.assertEqual(response.status_code, 500)
        self.assertTrue(response["Content-Type"].startswith("application/json"))
        payload = response.json()
        self.assertIn("error", payload)
        self.assertEqual(payload["error"]["code"], "internal_server_error")
