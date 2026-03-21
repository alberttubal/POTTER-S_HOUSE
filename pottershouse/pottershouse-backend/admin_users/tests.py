from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from rest_framework.test import APITestCase

from admin_users.models import AdminUser
from email_outbox.models import EmailOutbox


class AdminAuthApiTests(APITestCase):
    def setUp(self):
        self.admin = AdminUser.objects.create_superuser(
            email="admin-auth@example.com",
            password="AdminPass123!",
            full_name="Auth Admin",
        )

    def test_login_success_returns_access_token(self):
        response = self.client.post(
            "/api/v1/admin/login/",
            {"email": "admin-auth@example.com", "password": "AdminPass123!"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)
        self.assertIn(settings.REFRESH_COOKIE_NAME, response.cookies)

    def test_login_invalid_credentials_returns_401(self):
        response = self.client.post(
            "/api/v1/admin/login/",
            {"email": "admin-auth@example.com", "password": "wrong-password"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["error"]["code"], "invalid_credentials")

    def test_refresh_success_after_login(self):
        login = self.client.post(
            "/api/v1/admin/login/",
            {"email": "admin-auth@example.com", "password": "AdminPass123!"},
            format="json",
        )
        self.assertEqual(login.status_code, 200)

        refresh = self.client.post("/api/v1/admin/refresh/", {}, format="json")
        self.assertEqual(refresh.status_code, 200)
        self.assertIn("token", refresh.data)


class AdminPasswordApiTests(APITestCase):
    def setUp(self):
        self.admin = AdminUser.objects.create_superuser(
            email="admin-password@example.com",
            password="AdminPass123!",
            full_name="Password Admin",
        )

    def test_forgot_password_queues_email_for_existing_user(self):
        response = self.client.post(
            "/api/v1/admin/password/forgot/",
            {"email": self.admin.email},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EmailOutbox.objects.count(), 1)

        queued = EmailOutbox.objects.first()
        self.assertEqual(queued.to_email, self.admin.email)
        self.assertEqual(queued.template, "admin_password_reset")
        self.assertIn("reset_url", queued.payload)

    def test_forgot_password_does_not_reveal_unknown_email(self):
        response = self.client.post(
            "/api/v1/admin/password/forgot/",
            {"email": "unknown@example.com"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EmailOutbox.objects.count(), 0)

    def test_reset_password_with_valid_token(self):
        uid = urlsafe_base64_encode(force_bytes(self.admin.pk))
        token = PasswordResetTokenGenerator().make_token(self.admin)
        new_password = "PanelStrongPass123!"

        response = self.client.post(
            "/api/v1/admin/password/reset/",
            {"uid": uid, "token": token, "new_password": new_password},
            format="json",
        )
        self.assertEqual(response.status_code, 200)

        self.admin.refresh_from_db()
        self.assertTrue(self.admin.check_password(new_password))
