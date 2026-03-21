import { clearToken, getToken, setToken } from "./auth";

const API_BASE = "/api/v1";

export class ApiError extends Error {
  status: number;
  data: unknown;

  constructor(status: number, data: unknown, message: string) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

export type PaginatedResponse<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};

export type PackageDTO = {
  id: string;
  name: string;
  description: string;
  price: string;
  active: boolean;
  created_at: string;
  updated_at: string;
};

export type BookingStatus = "confirmed" | "cancelled";

export type BookingWorkflowStatus =
  | "new"
  | "contacted"
  | "confirmed"
  | "paid"
  | "completed"
  | "cancelled";

export type BookingDTO = {
  id: string;
  customer_name: string;
  phone: string;
  email: string;
  event_type: string;
  event_date_start: string;
  event_date_end: string;
  event_all_day: boolean;
  guests: number;
  package_id: string | null;
  dietary_needs: string;
  notes: string;
  status: BookingStatus;
  workflow_status: BookingWorkflowStatus;
  deposit_paid: boolean;
  created_at: string;
  updated_at: string;
};

export type BookingPayload = {
  customer_name: string;
  phone: string;
  email: string;
  event_type: string;
  event_date_start: string;
  event_date_end: string;
  event_all_day: boolean;
  guests: number;
  package_id?: string | null;
  notes?: string;
  dietary_needs?: string;
  honeypot: string;
};

export type TestimonialDTO = {
  id: string;
  customer_name: string;
  content: string;
  published: boolean;
  created_at: string;
  updated_at: string;
};

export type FaqDTO = {
  id: string;
  question: string;
  answer: string;
  published: boolean;
  created_at: string;
  updated_at: string;
};

export type SettingDTO = {
  id: string;
  key: string;
  value: unknown;
  created_at: string;
  updated_at: string;
};

export type UploadDTO = {
  id: string;
  key: string;
  url: string;
  size: number;
  mime_type: string;
  alt_text: string | null;
  published: boolean;
  created_at: string;
  updated_at: string;
};

type AdminBookingsQuery = {
  page?: number;
  pageSize?: number;
  q?: string;
  status?: string;
  from?: string;
  to?: string;
};

function normalizePath(path: string) {
  return path.startsWith("/") ? path : `/${path}`;
}

function withTrailingSlash(path: string) {
  return path.endsWith("/") ? path : `${path}/`;
}

function authHeaders(): Record<string, string> {
  const token = getToken();
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
}


function buildQuery(query: Record<string, string | number | undefined>) {
  const params = new URLSearchParams();
  Object.entries(query).forEach(([key, value]) => {
    if (value === undefined) return;
    const stringValue = String(value).trim();
    if (!stringValue) return;
    params.set(key, stringValue);
  });
  const encoded = params.toString();
  return encoded ? `?${encoded}` : "";
}

async function requestJson(path: string, options: RequestInit = {}, allowRefresh = true) {
  const target = `${API_BASE}${normalizePath(path)}`;
  const response = await fetch(target, {
    credentials: "include",
    ...options
  });

  const text = await response.text();
  let data: unknown = null;

  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }

  const authHeader = options.headers
    ? new Headers(options.headers as HeadersInit).get("Authorization")
    : null;

  if (
    response.status === 401 &&
    allowRefresh &&
    !!authHeader &&
    !target.includes("/admin/refresh/")
  ) {
    try {
      const refreshed = await adminRefresh();
      const token = (refreshed as { token?: string } | null)?.token;
      if (token) {
        setToken(token);
        return requestJson(path, options, false);
      }
      clearToken();
    } catch {
      clearToken();
    }
  }

  if (!response.ok) {
    const retryAfter = response.headers.get("Retry-After");
    if (
      retryAfter &&
      data &&
      typeof data === "object" &&
      !Array.isArray(data) &&
      !("retryAfter" in data)
    ) {
      (data as Record<string, unknown>).retryAfter = retryAfter;
    }

    const parsed = data as { error?: { message?: string }; message?: string } | null;
    const message =
      parsed?.error?.message ||
      parsed?.message ||
      response.statusText ||
      "Request failed";
    throw new ApiError(response.status, data, message);
  }

  return data;
}

export function unwrapResults<T>(value: unknown): T[] {
  if (Array.isArray(value)) {
    return value as T[];
  }
  const page = value as Partial<PaginatedResponse<T>> | null;
  if (Array.isArray(page?.results)) {
    return page.results;
  }
  return [];
}

export async function createBooking(payload: BookingPayload, idempotencyKey: string) {
  return requestJson(withTrailingSlash("/bookings"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Idempotency-Key": idempotencyKey
    },
    body: JSON.stringify(payload)
  });
}

export async function fetchHealth() {
  return requestJson("/health/");
}

export async function adminLogin(email: string, password: string) {
  return requestJson("/admin/login/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  }, false);
}

export async function adminRefresh() {
  return requestJson("/admin/refresh/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({})
  }, false);
}

export async function adminPasswordForgot(email: string) {
  return requestJson("/admin/password/forgot/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email })
  }, false);
}

export async function adminPasswordReset(uid: string, token: string, new_password: string) {
  return requestJson("/admin/password/reset/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ uid, token, new_password })
  }, false);
}

export async function fetchAdminBookings(query: AdminBookingsQuery = {}) {
  const qs = buildQuery({
    page: query.page,
    pageSize: query.pageSize,
    q: query.q,
    status: query.status,
    from: query.from,
    to: query.to
  });
  return requestJson(`/admin/bookings/${qs}`, {
    headers: { ...authHeaders() }
  }) as Promise<PaginatedResponse<BookingDTO>>;
}

export async function fetchAdminBooking(id: string) {
  return requestJson(`/admin/bookings/${id}/`, {
    headers: { ...authHeaders() }
  }) as Promise<BookingDTO>;
}

export async function updateAdminBooking(id: string, payload: Partial<BookingDTO>) {
  return requestJson(`/admin/bookings/${id}/`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(payload)
  }) as Promise<BookingDTO>;
}

export async function fetchPublicPackages(page = 1, pageSize = 12, active = true) {
  const qs = buildQuery({ page, pageSize, active: String(active) });
  return requestJson(`/packages/${qs}`) as Promise<PaginatedResponse<PackageDTO>>;
}

export async function fetchPublicPackage(id: string) {
  return requestJson(`/packages/${id}/`) as Promise<PackageDTO>;
}

export async function fetchAdminPackages() {
  return requestJson("/admin/packages/", {
    headers: { ...authHeaders() }
  }) as Promise<PackageDTO[]>;
}

export async function createAdminPackage(payload: {
  name: string;
  description?: string;
  price: number;
  active: boolean;
}) {
  return requestJson("/admin/packages/", {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(payload)
  }) as Promise<PackageDTO>;
}

export async function fetchPublicTestimonials() {
  return requestJson("/testimonials/") as Promise<TestimonialDTO[]>;
}

export async function fetchAdminTestimonials() {
  return requestJson("/admin/testimonials/", {
    headers: { ...authHeaders() }
  }) as Promise<TestimonialDTO[]>;
}

export async function fetchPublicSettings() {
  return requestJson("/settings/") as Promise<SettingDTO[]>;
}

export async function fetchPublicFaqs() {
  return requestJson("/faqs/") as Promise<FaqDTO[]>;
}

export async function fetchAdminFaqs() {
  return requestJson("/admin/faqs/", {
    headers: { ...authHeaders() }
  }) as Promise<FaqDTO[]>;
}

export async function createAdminFaq(payload: {
  question: string;
  answer: string;
  published: boolean;
}) {
  return requestJson("/admin/faqs/", {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(payload)
  }) as Promise<FaqDTO>;
}

export async function createAdminTestimonial(payload: {
  customer_name: string;
  content: string;
  published: boolean;
}) {
  return requestJson("/admin/testimonials/", {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(payload)
  }) as Promise<TestimonialDTO>;
}

export async function fetchPublicGallery() {
  return requestJson("/gallery/") as Promise<UploadDTO[]>;
}

export async function uploadImages(files: File[]) {
  const form = new FormData();
  files.forEach((file) => form.append("files", file));
  return requestJson("/admin/uploads/", {
    method: "POST",
    headers: { ...authHeaders() },
    body: form
  }) as Promise<{
    urls: Array<{
      url: string;
      key: string;
      size: number;
      alt_text: string | null;
      published: boolean;
    }>;
  }>;
}

export async function fetchAdminUploadsList() {
  return requestJson("/admin/uploads/list/", {
    headers: { ...authHeaders() }
  }) as Promise<UploadDTO[]>;
}

export async function updateAdminUpload(
  id: string,
  payload: Partial<Pick<UploadDTO, "alt_text" | "published">>
) {
  return requestJson(`/admin/uploads/${id}/`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(payload)
  }) as Promise<UploadDTO>;
}

export async function fetchAdminSettings() {
  return requestJson("/admin/settings/", {
    headers: { ...authHeaders() }
  }) as Promise<SettingDTO[]>;
}

export async function createAdminSetting(payload: { key: string; value: unknown }) {
  return requestJson("/admin/settings/", {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(payload)
  }) as Promise<SettingDTO>;
}

export async function updateAdminSetting(id: string, payload: { key?: string; value: unknown }) {
  return requestJson(`/admin/settings/${id}/`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(payload)
  }) as Promise<SettingDTO>;
}

// Backward-compatible aliases while we migrate old callers.
export async function fetchTestimonials() {
  return fetchAdminTestimonials();
}

export async function saveTestimonial(payload: {
  customer_name?: string;
  content?: string;
  published?: boolean;
  author?: string;
  quote?: string;
}) {
  return createAdminTestimonial({
    customer_name: payload.customer_name ?? payload.author ?? "",
    content: payload.content ?? payload.quote ?? "",
    published: payload.published ?? false
  });
}

export async function fetchSettings() {
  return fetchAdminSettings();
}

export async function saveSettings(payload: { key: string; value: unknown }) {
  return createAdminSetting(payload);
}

export async function uploadImage(file: File) {
  return uploadImages([file]);
}
