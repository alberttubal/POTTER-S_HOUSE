#!/usr/bin/env python
"""
One-command backend smoke test for panel/demo runs.

Usage:
  python scripts/panel_backend_smoke.py --base-url http://127.0.0.1:8000 --admin-email admin@example.com --admin-password AdminPass123!
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import requests


class SmokeError(RuntimeError):
    pass


def iso_z(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def short(value: str, size: int = 8) -> str:
    return value[:size]


@dataclass
class SmokeContext:
    base_url: str
    admin_email: str
    admin_password: str
    timeout: int

    def __post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/")
        self.session = requests.Session()
        self.token: str | None = None

        self.booking_id: str | None = None
        self.booking_idempotency_key: str | None = None
        self.booking_payload: dict[str, Any] | None = None

        self.package_id: str | None = None
        self.testimonial_id: str | None = None
        self.faq_id: str | None = None
        self.setting_id: str | None = None
        self.upload_id: str | None = None
        self.upload_key: str | None = None

    def url(self, path: str) -> str:
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self.base_url}{path}"

    def request(self, method: str, path: str, *, auth: bool = False, **kwargs: Any) -> requests.Response:
        headers = dict(kwargs.pop("headers", {}) or {})
        if auth:
            if not self.token:
                raise SmokeError("Missing admin token. Login step likely failed.")
            headers["Authorization"] = f"Bearer {self.token}"
        response = self.session.request(
            method=method,
            url=self.url(path),
            headers=headers,
            timeout=self.timeout,
            **kwargs,
        )
        return response

    @staticmethod
    def assert_status(response: requests.Response, expected: int, label: str) -> None:
        if response.status_code != expected:
            raise SmokeError(
                f"{label}: expected HTTP {expected}, got {response.status_code}. Body: {response.text[:500]}"
            )

    @staticmethod
    def parse_json(response: requests.Response, label: str) -> dict[str, Any] | list[Any]:
        try:
            return response.json()
        except Exception as exc:  # pragma: no cover - defensive
            raise SmokeError(f"{label}: response is not valid JSON. Body: {response.text[:500]}") from exc


def step(label: str, fn) -> None:
    print(f"\n[RUN] {label}")
    fn()
    print(f"[OK ] {label}")


def run_health(ctx: SmokeContext) -> None:
    response = ctx.request("GET", "/api/v1/health/")
    ctx.assert_status(response, 200, "Health")
    data = ctx.parse_json(response, "Health")
    if not isinstance(data, dict) or data.get("status") != "ok":
        raise SmokeError(f"Health: unexpected payload {data}")


def run_login(ctx: SmokeContext) -> None:
    response = ctx.request(
        "POST",
        "/api/v1/admin/login/",
        json={"email": ctx.admin_email, "password": ctx.admin_password},
    )
    ctx.assert_status(response, 200, "Admin Login")
    data = ctx.parse_json(response, "Admin Login")
    if not isinstance(data, dict) or not data.get("token"):
        raise SmokeError(f"Admin Login: token missing in response {data}")
    ctx.token = str(data["token"])


def run_refresh(ctx: SmokeContext) -> None:
    response = ctx.request("POST", "/api/v1/admin/refresh/", json={})
    ctx.assert_status(response, 200, "Admin Refresh")
    data = ctx.parse_json(response, "Admin Refresh")
    if not isinstance(data, dict) or not data.get("token"):
        raise SmokeError(f"Admin Refresh: token missing in response {data}")


def run_public_booking_and_idempotency(ctx: SmokeContext) -> None:
    booking_id: str | None = None
    payload: dict[str, Any] | None = None
    idem_key: str | None = None

    base_start = datetime.now(timezone.utc) + timedelta(days=30)

    for attempt in range(1, 6):
        start = base_start + timedelta(hours=attempt * 3)
        end = start + timedelta(hours=2)
        idem_key = f"panel-smoke-{uuid.uuid4()}"
        payload = {
            "customer_name": f"Panel Smoke {short(str(uuid.uuid4()))}",
            "phone": "09170000000",
            "email": f"panel-smoke-{short(str(uuid.uuid4()))}@example.com",
            "event_type": "corporate",
            "event_date_start": iso_z(start),
            "event_date_end": iso_z(end),
            "event_all_day": False,
            "guests": 50,
            "honeypot": "",
        }

        first = ctx.request(
            "POST",
            "/api/v1/bookings/",
            headers={"Idempotency-Key": idem_key},
            json=payload,
        )

        if first.status_code == 201:
            first_json = ctx.parse_json(first, "Create Booking")
            if not isinstance(first_json, dict) or not first_json.get("id"):
                raise SmokeError(f"Create Booking: missing booking id {first_json}")
            booking_id = str(first_json["id"])
            break

        if first.status_code != 409:
            ctx.assert_status(first, 201, "Create Booking")

    if not booking_id or not payload or not idem_key:
        raise SmokeError("Create Booking: no conflict-free slot found after retries.")

    second = ctx.request(
        "POST",
        "/api/v1/bookings/",
        headers={"Idempotency-Key": idem_key},
        json=payload,
    )
    ctx.assert_status(second, 201, "Replay Booking (Idempotency)")
    second_json = ctx.parse_json(second, "Replay Booking (Idempotency)")
    if not isinstance(second_json, dict) or str(second_json.get("id")) != booking_id:
        raise SmokeError(
            "Replay Booking (Idempotency): booking id mismatch. "
            f"expected {booking_id}, got {second_json}"
        )

    ctx.booking_id = booking_id
    ctx.booking_idempotency_key = idem_key
    ctx.booking_payload = payload


def run_admin_booking_checks(ctx: SmokeContext) -> None:
    if not ctx.booking_id:
        raise SmokeError("Admin booking checks: booking_id is missing")

    listing = ctx.request("GET", "/api/v1/admin/bookings/?page=1&pageSize=10", auth=True)
    ctx.assert_status(listing, 200, "Admin Bookings List")
    list_json = ctx.parse_json(listing, "Admin Bookings List")
    if not isinstance(list_json, dict) or "results" not in list_json:
        raise SmokeError(f"Admin Bookings List: unexpected payload {list_json}")

    detail = ctx.request("GET", f"/api/v1/admin/bookings/{ctx.booking_id}/", auth=True)
    ctx.assert_status(detail, 200, "Admin Booking Detail")
    detail_json = ctx.parse_json(detail, "Admin Booking Detail")
    if not isinstance(detail_json, dict) or str(detail_json.get("id")) != ctx.booking_id:
        raise SmokeError(f"Admin Booking Detail: unexpected payload {detail_json}")

    patch = ctx.request(
        "PATCH",
        f"/api/v1/admin/bookings/{ctx.booking_id}/",
        auth=True,
        json={"workflow_status": "contacted"},
    )
    ctx.assert_status(patch, 200, "Admin Booking Update")
    patch_json = ctx.parse_json(patch, "Admin Booking Update")
    if not isinstance(patch_json, dict) or patch_json.get("workflow_status") != "contacted":
        raise SmokeError(f"Admin Booking Update: workflow_status not updated {patch_json}")

    csv_response = ctx.request("GET", "/api/v1/admin/bookings.csv", auth=True)
    ctx.assert_status(csv_response, 200, "Admin Bookings CSV")
    content_type = csv_response.headers.get("Content-Type", "")
    if "text/csv" not in content_type:
        raise SmokeError(f"Admin Bookings CSV: unexpected content-type {content_type}")


def run_packages_flow(ctx: SmokeContext) -> None:
    public_list = ctx.request("GET", "/api/v1/packages/?page=1&pageSize=5&active=true")
    ctx.assert_status(public_list, 200, "Packages Public List")
    public_list_json = ctx.parse_json(public_list, "Packages Public List")
    if not isinstance(public_list_json, dict) or "results" not in public_list_json:
        raise SmokeError(f"Packages Public List: unexpected payload {public_list_json}")

    package_name = f"Panel Smoke Package {short(str(uuid.uuid4()))}"
    create = ctx.request(
        "POST",
        "/api/v1/admin/packages/",
        auth=True,
        json={
            "name": package_name,
            "description": "Created by smoke test",
            "price": 1234.56,
            "active": True,
        },
    )
    ctx.assert_status(create, 201, "Packages Admin Create")
    create_json = ctx.parse_json(create, "Packages Admin Create")
    if not isinstance(create_json, dict) or not create_json.get("id"):
        raise SmokeError(f"Packages Admin Create: unexpected payload {create_json}")
    package_id = str(create_json["id"])
    ctx.package_id = package_id

    public_detail = ctx.request("GET", f"/api/v1/packages/{package_id}/")
    ctx.assert_status(public_detail, 200, "Packages Public Detail")
    public_detail_json = ctx.parse_json(public_detail, "Packages Public Detail")
    if not isinstance(public_detail_json, dict) or str(public_detail_json.get("id")) != package_id:
        raise SmokeError(f"Packages Public Detail: unexpected payload {public_detail_json}")


def run_testimonials_flow(ctx: SmokeContext) -> None:
    create = ctx.request(
        "POST",
        "/api/v1/admin/testimonials/",
        auth=True,
        json={
            "customer_name": f"Panel Client {short(str(uuid.uuid4()))}",
            "content": "Panel smoke testimonial content.",
            "published": True,
        },
    )
    ctx.assert_status(create, 201, "Testimonials Admin Create")
    create_json = ctx.parse_json(create, "Testimonials Admin Create")
    if not isinstance(create_json, dict) or not create_json.get("id"):
        raise SmokeError(f"Testimonials Admin Create: unexpected payload {create_json}")
    ctx.testimonial_id = str(create_json["id"])

    public_list = ctx.request("GET", "/api/v1/testimonials/")
    ctx.assert_status(public_list, 200, "Testimonials Public List")
    public_json = ctx.parse_json(public_list, "Testimonials Public List")
    if not isinstance(public_json, list):
        raise SmokeError(f"Testimonials Public List: unexpected payload {public_json}")


def run_faqs_flow(ctx: SmokeContext) -> None:
    create = ctx.request(
        "POST",
        "/api/v1/admin/faqs/",
        auth=True,
        json={
            "question": f"Panel smoke question {short(str(uuid.uuid4()))}?",
            "answer": "Panel smoke answer.",
            "published": True,
        },
    )
    ctx.assert_status(create, 201, "FAQs Admin Create")
    create_json = ctx.parse_json(create, "FAQs Admin Create")
    if not isinstance(create_json, dict) or not create_json.get("id"):
        raise SmokeError(f"FAQs Admin Create: unexpected payload {create_json}")
    ctx.faq_id = str(create_json["id"])

    public_list = ctx.request("GET", "/api/v1/faqs/")
    ctx.assert_status(public_list, 200, "FAQs Public List")
    public_json = ctx.parse_json(public_list, "FAQs Public List")
    if not isinstance(public_json, list):
        raise SmokeError(f"FAQs Public List: unexpected payload {public_json}")


def run_settings_flow(ctx: SmokeContext) -> None:
    key = f"panel_smoke_{short(str(uuid.uuid4()))}"
    create = ctx.request(
        "POST",
        "/api/v1/admin/settings/",
        auth=True,
        json={"key": key, "value": {"ok": True}},
    )
    ctx.assert_status(create, 201, "Settings Admin Create")
    create_json = ctx.parse_json(create, "Settings Admin Create")
    if not isinstance(create_json, dict) or not create_json.get("id"):
        raise SmokeError(f"Settings Admin Create: unexpected payload {create_json}")
    setting_id = str(create_json["id"])
    ctx.setting_id = setting_id

    patch = ctx.request(
        "PATCH",
        f"/api/v1/admin/settings/{setting_id}/",
        auth=True,
        json={"value": {"ok": True, "updated": True}},
    )
    ctx.assert_status(patch, 200, "Settings Admin Update")
    patch_json = ctx.parse_json(patch, "Settings Admin Update")
    if not isinstance(patch_json, dict) or not isinstance(patch_json.get("value"), dict):
        raise SmokeError(f"Settings Admin Update: unexpected payload {patch_json}")

    listing = ctx.request("GET", "/api/v1/admin/settings/", auth=True)
    ctx.assert_status(listing, 200, "Settings Admin List")
    list_json = ctx.parse_json(listing, "Settings Admin List")
    if not isinstance(list_json, list):
        raise SmokeError(f"Settings Admin List: unexpected payload {list_json}")
    if not any(isinstance(item, dict) and str(item.get("id")) == setting_id for item in list_json):
        raise SmokeError("Settings Admin List: created setting not found")


def run_uploads_flow(ctx: SmokeContext) -> None:
    # 1x1 transparent PNG bytes
    png = (
        b"\x89PNG\r\n\x1a\n"
        b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
        b"\x00\x00\x00\x0cIDATx\x9cc```\x00\x00\x00\x04\x00\x01\xf6\x17\x38U"
        b"\x00\x00\x00\x00IEND\xaeB`\x82"
    )

    create = ctx.request(
        "POST",
        "/api/v1/admin/uploads/",
        auth=True,
        files={"files": ("panel-smoke.png", png, "image/png")},
    )
    ctx.assert_status(create, 201, "Uploads Admin Create")
    create_json = ctx.parse_json(create, "Uploads Admin Create")
    urls = create_json.get("urls") if isinstance(create_json, dict) else None
    if not isinstance(urls, list) or not urls:
        raise SmokeError(f"Uploads Admin Create: unexpected payload {create_json}")
    upload_key = str(urls[0].get("key"))
    if not upload_key:
        raise SmokeError(f"Uploads Admin Create: missing key {create_json}")
    ctx.upload_key = upload_key

    listing = ctx.request("GET", "/api/v1/admin/uploads/list/", auth=True)
    ctx.assert_status(listing, 200, "Uploads Admin List")
    list_json = ctx.parse_json(listing, "Uploads Admin List")
    if not isinstance(list_json, list):
        raise SmokeError(f"Uploads Admin List: unexpected payload {list_json}")

    matched = next(
        (
            item
            for item in list_json
            if isinstance(item, dict) and str(item.get("key")) == upload_key
        ),
        None,
    )
    if not matched or not matched.get("id"):
        raise SmokeError(f"Uploads Admin List: uploaded key not found ({upload_key})")
    upload_id = str(matched["id"])
    ctx.upload_id = upload_id

    patch = ctx.request(
        "PATCH",
        f"/api/v1/admin/uploads/{upload_id}/",
        auth=True,
        json={"alt_text": "Panel smoke image", "published": True},
    )
    ctx.assert_status(patch, 200, "Uploads Admin Update")
    patch_json = ctx.parse_json(patch, "Uploads Admin Update")
    if not isinstance(patch_json, dict) or patch_json.get("published") is not True:
        raise SmokeError(f"Uploads Admin Update: unexpected payload {patch_json}")

    public_gallery = ctx.request("GET", "/api/v1/gallery/")
    ctx.assert_status(public_gallery, 200, "Gallery Public List")
    gallery_json = ctx.parse_json(public_gallery, "Gallery Public List")
    if not isinstance(gallery_json, list):
        raise SmokeError(f"Gallery Public List: unexpected payload {gallery_json}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one-go backend smoke tests for panel/demo.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Backend base URL")
    parser.add_argument("--admin-email", required=True, help="Admin email for login")
    parser.add_argument("--admin-password", required=True, help="Admin password for login")
    parser.add_argument("--timeout", type=int, default=20, help="HTTP timeout in seconds per request")
    args = parser.parse_args()

    ctx = SmokeContext(
        base_url=args.base_url,
        admin_email=args.admin_email,
        admin_password=args.admin_password,
        timeout=args.timeout,
    )

    try:
        step("Health", lambda: run_health(ctx))
        step("Admin Login", lambda: run_login(ctx))
        step("Admin Refresh", lambda: run_refresh(ctx))
        step("Public Booking + Idempotency Replay", lambda: run_public_booking_and_idempotency(ctx))
        step("Admin Booking List/Detail/Update/CSV", lambda: run_admin_booking_checks(ctx))
        step("Packages Public + Admin Create + Public Detail", lambda: run_packages_flow(ctx))
        step("Testimonials Admin Create + Public List", lambda: run_testimonials_flow(ctx))
        step("FAQs Admin Create + Public List", lambda: run_faqs_flow(ctx))
        step("Settings Admin Create/Update/List", lambda: run_settings_flow(ctx))
        step("Uploads Admin Create/List/Update + Public Gallery", lambda: run_uploads_flow(ctx))
    except Exception as exc:
        print(f"\n[FAIL] {exc}")
        return 1

    summary = {
        "booking_id": ctx.booking_id,
        "package_id": ctx.package_id,
        "testimonial_id": ctx.testimonial_id,
        "faq_id": ctx.faq_id,
        "setting_id": ctx.setting_id,
        "upload_id": ctx.upload_id,
        "upload_key": ctx.upload_key,
    }
    print("\n[PASS] All smoke checks completed.")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
