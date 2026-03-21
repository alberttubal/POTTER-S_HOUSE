from decimal import Decimal

from rest_framework.test import APITestCase

from admin_users.models import AdminUser
from packages.models import Package


class PackagePublicApiTests(APITestCase):
    def setUp(self):
        self.active_pkg = Package.objects.create(
            name="Buffet A",
            description="Active package",
            price=Decimal("250.00"),
            active=True,
        )
        self.inactive_pkg = Package.objects.create(
            name="Buffet B",
            description="Inactive package",
            price=Decimal("350.00"),
            active=False,
        )

    def test_public_list_can_filter_active_true(self):
        response = self.client.get("/api/v1/packages/?active=true&page=1&pageSize=10")
        self.assertEqual(response.status_code, 200)

        results = response.data.get("results", [])
        ids = {item["id"] for item in results}
        self.assertIn(str(self.active_pkg.id), ids)
        self.assertNotIn(str(self.inactive_pkg.id), ids)

    def test_public_detail_returns_package(self):
        response = self.client.get(f"/api/v1/packages/{self.active_pkg.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], str(self.active_pkg.id))
        self.assertEqual(response.data["name"], "Buffet A")


class PackageAdminApiTests(APITestCase):
    def setUp(self):
        self.admin = AdminUser.objects.create_superuser(
            email="packages-admin@example.com",
            password="AdminPass123!",
            full_name="Packages Admin",
        )

    def test_admin_create_package(self):
        self.client.force_authenticate(user=self.admin)
        payload = {
            "name": "Panel Package",
            "description": "Created from tests",
            "price": "999.00",
            "active": True,
        }
        response = self.client.post("/api/v1/admin/packages/", payload, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Package.objects.count(), 1)
        self.assertEqual(response.data["name"], payload["name"])

    def test_admin_list_requires_auth(self):
        response = self.client.get("/api/v1/admin/packages/")
        self.assertIn(response.status_code, {401, 403})
