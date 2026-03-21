from rest_framework.test import APITestCase

from admin_users.models import AdminUser
from settings_app.models import Setting


class SettingPublicApiTests(APITestCase):
    def setUp(self):
        Setting.objects.create(key="contact_phone", value="09170000000")
        Setting.objects.create(key="business_address", value="Cebu City")
        Setting.objects.create(key="internal_secret", value="do-not-expose")

    def test_public_settings_only_exposes_whitelisted_keys(self):
        response = self.client.get("/api/v1/settings/")
        self.assertEqual(response.status_code, 200)

        keys = {row["key"] for row in response.data}
        self.assertIn("contact_phone", keys)
        self.assertIn("business_address", keys)
        self.assertNotIn("internal_secret", keys)


class SettingAdminApiTests(APITestCase):
    def setUp(self):
        self.admin = AdminUser.objects.create_superuser(
            email="settings-admin@example.com",
            password="AdminPass123!",
            full_name="Settings Admin",
        )

    def test_admin_create_and_update_setting(self):
        self.client.force_authenticate(user=self.admin)

        create_response = self.client.post(
            "/api/v1/admin/settings/",
            {"key": "contact_phone", "value": "09990000000"},
            format="json",
        )
        self.assertEqual(create_response.status_code, 201)
        setting_id = create_response.data["id"]

        patch_response = self.client.patch(
            f"/api/v1/admin/settings/{setting_id}/",
            {"value": "09180000000"},
            format="json",
        )
        self.assertEqual(patch_response.status_code, 200)
        self.assertEqual(patch_response.data["value"], "09180000000")

    def test_admin_list_requires_auth(self):
        response = self.client.get("/api/v1/admin/settings/")
        self.assertIn(response.status_code, {401, 403})
