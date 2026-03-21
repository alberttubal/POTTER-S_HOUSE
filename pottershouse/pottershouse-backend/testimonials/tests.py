from rest_framework.test import APITestCase

from admin_users.models import AdminUser
from testimonials.models import Testimonial


class TestimonialPublicApiTests(APITestCase):
    def setUp(self):
        Testimonial.objects.create(
            customer_name="Published Client",
            content="Published testimonial",
            published=True,
        )
        Testimonial.objects.create(
            customer_name="Draft Client",
            content="Draft testimonial",
            published=False,
        )

    def test_public_list_returns_only_published(self):
        response = self.client.get("/api/v1/testimonials/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["customer_name"], "Published Client")


class TestimonialAdminApiTests(APITestCase):
    def setUp(self):
        self.admin = AdminUser.objects.create_superuser(
            email="testimonials-admin@example.com",
            password="AdminPass123!",
            full_name="Testimonials Admin",
        )

    def test_admin_create_testimonial(self):
        self.client.force_authenticate(user=self.admin)
        payload = {
            "customer_name": "Panel Client",
            "content": "Great service",
            "published": True,
        }
        response = self.client.post("/api/v1/admin/testimonials/", payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Testimonial.objects.count(), 1)
        self.assertEqual(response.data["customer_name"], "Panel Client")

    def test_admin_list_requires_auth(self):
        response = self.client.get("/api/v1/admin/testimonials/")
        self.assertIn(response.status_code, {401, 403})
