from rest_framework.test import APITestCase

from admin_users.models import AdminUser
from faqs.models import FAQ


class FAQPublicApiTests(APITestCase):
    def setUp(self):
        FAQ.objects.create(question="Published FAQ?", answer="Yes", published=True)
        FAQ.objects.create(question="Draft FAQ?", answer="No", published=False)

    def test_public_list_returns_only_published(self):
        response = self.client.get("/api/v1/faqs/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["question"], "Published FAQ?")


class FAQAdminApiTests(APITestCase):
    def setUp(self):
        self.admin = AdminUser.objects.create_superuser(
            email="faq-admin@example.com",
            password="AdminPass123!",
            full_name="FAQ Admin",
        )

    def test_admin_create_faq(self):
        self.client.force_authenticate(user=self.admin)
        payload = {
            "question": "How long is delivery?",
            "answer": "Delivery window is discussed per booking.",
            "published": True,
        }
        response = self.client.post("/api/v1/admin/faqs/", payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(FAQ.objects.count(), 1)
        self.assertEqual(response.data["question"], payload["question"])

    def test_admin_list_requires_auth(self):
        response = self.client.get("/api/v1/admin/faqs/")
        self.assertIn(response.status_code, {401, 403})
