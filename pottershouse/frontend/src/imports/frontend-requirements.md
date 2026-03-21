FRONTEND REQUIREMENTS:
Potter's House — Final polished FRONTEND requirements
Below are production-ready, testable frontend requirements you can hand to your UI developer / QA. They are precise, measurable, and mapped to the API contract the frontend will consume.
________________________________________
1) Overview / purpose
Build a mobile-first, brand-aligned (red / white) web application that lets customers browse packages, submit booking/quote requests, and lets the owner/admin manage content via a secure admin UI. The frontend must be performant (primary pages ≤ 3s on a mid-range phone on a mobile network), accessible (WCAG AA where feasible), and robust against form abuse.
________________________________________
2) General UI/UX guidelines
•	Branding: apply client-provided assets (logo, exact red/white values). If missing, use a single primary red and white palette and expose CSS variables for easy replacement.
•	Design system: component-based (buttons, inputs, cards, modals, toasts) with documented CSS variables and spacing scale.
•	Framework: React (recommended) or Vue/Angular acceptable. Use TypeScript.
•	Styling: utility-first (Tailwind) or component CSS modules. Include a small theme file.
•	Responsive breakpoints: mobile-first; suggested breakpoints: 0–639px (mobile), 640–1023px (tablet), ≥1024px (desktop).
•	Accessibility: semantic HTML, keyboard focus states, aria-* where required, images with alt, color contrast WCAG AA.
•	Localization-ready: text strings in a single translation file (even if initial app in one language).
________________________________________
6.2 Frontend Requirements (full)
Framework & Tooling
•	Stack: React + TypeScript; Vite or Next.js (SSG for public pages, server components optional for admin); Tailwind CSS; Jest + RTL for unit tests; Playwright for E2E; Lighthouse CI for performance.
•	Repo path: repo/frontend/
•	Entry points: / (Home), /packages, /packages/:id, /gallery, /contact (contains booking form), /admin/*.
•	Design: CSS variables for brand colors; accessible tokens; component library at repo/frontend/src/components.
Pages & components (deliverable-ready)
•	Home — hero (inline critical CSS), featured PackageCarousel, testimonials preview.
o	Acceptance: LCP portion ≤1.5s in Lighthouse test.
•	/packages — grid of PackageCard components. Pagination or infinite scroll (pagination recommended: ?page=N&pageSize=12).
•	/packages/:id — large image carousel (accessible), description, "Request Quote / Book" CTA scrolls to booking form.
•	/gallery — responsive grid, lazy-load images.
•	/contact — Contact info + BookingForm.
•	/admin/ — login, dashboard, bookings list (filterable), booking detail, packages manager (Add/Edit/Publish), uploads manager, testimonials/FAQ manager, settings.
BookingForm (fields & client validations — exact)
Fields:
•	customer_name (required, string, max 255)
•	phone (required, string; validate E.164 as preferred but accept local formats)
•	email (required, valid email)
•	event_type (required, select)
•	event_date_start (required, datetime picker with timezone +08:00) frontend must convert all incoming UTC timestamps from the API into Asia/Manila (+08:00) before displaying them in the admin dashboard or customer views
•	event_date_end (required, datetime picker; >= start)
•	event_all_day (boolean)
•	guests (required, integer > 0)
•	package_id (optional, UUID)
•	notes (optional, string)
•	dietary_needs (optional, string)
•	deposit_paid (false on submit — controlled by admin)
•	a hidden honeypot field (backends+’s anti abuse)
Client validation rules:
•	event_date_start must be in the future relative to client clock; event_date_end >= event_date_start.
•	FE sends datetimes as ISO8601 with +08:00. Convert user input from local timezone to that format. frontend must convert all incoming UTC timestamps from the API into Asia/Manila (+08:00) before displaying them in the admin dashboard or customer views
•	Prevent double submit: disable submit and show spinner after first submission.
•	File inputs (admin only): accept image/jpeg, image/png, image/webp, file size ≤5MB.
UX for server responses (exact behavior)
•	201 Created: show success modal with booking ref (server bookingId), copyable details and WhatsApp link https://wa.me/<owner_phone>?text=<prepopulated>. Clear form.
•	400 Validation: map error.details[] to field-level messages; show toast summary.
•	401/403 admin endpoints: redirect to login; show message "Please sign in to access this area."
•	409 Conflict (Policy A): open conflict modal with error.conflictingBookings[] and error.suggested_alternatives[]. Provide action buttons to pick an alternative or edit dates. DO NOT present "force submit" for MVP.
•	429 Rate limited: show "Too many requests — try again after <Retry-After> seconds" and disable booking button for Retry-After seconds.
•	500: show friendly message "Server error — please try again later" and clickable contact options.
•	frontend must specifically parse the singular error root key (e.g., error.details[]) to ensure consistent field-level error mapping.
Performance targets & CI
•	Primary pages load ≤3.0s under Lighthouse (Moto G4, CPU x4 slowdown, Slow 4G). CI pipeline runs Lighthouse CI on staging and fails build on regressions.
•	Initial JS bundle ≤300 KB gzipped recommended; use route code-splitting.
Accessibility & tests
•	WCAG AA contrast, keyboard focusable interactive elements, aria labels, alt text required.
•	Admin UI forces alt_text on image upload modal (client validation).
•	Include automated Playwright E2E that verifies keyboard tab order on booking form and that aria-* attributes exist for form controls.
API calls & expected JSON error formats
•	All FE calls use base path /api/v1 (CORS allowed origins below). All responses including errors must match canonical wrapper (see §8).
•	Required headers (public booking):
- Content-Type: application/json (except multipart)
- Idempotency-Key: <uuid-or-string> — REQUIRED for ALL POST /api/v1/bookings requests. If the header is missing, the API will return 400 with machine code "missing_idempotency_key". FE must generate a stable UUID per distinct submission and reuse it only for safe retries of the same payload.
•	Required headers (admin):
- Authorization: Bearer <token> for all admin endpointsCORS origins: https://staging.pottershouse.example.com, https://pottershouse.example.com.
Accessibility test hook & health
•	Provide /health-ui that hits /api/v1/health and shows online/offline.
Measurable FE acceptance criteria (examples mapped)
•	Package publish loop: Admin publishes package → FE shows package on public /packages?active=true within 60s (owner: Both — FE displays, BE ensures cache invalidation).
•	Booking submission loop: POST /bookings returns 201 → admin list shows booking within 30s (owner: Both).
•	When workflow_status = 'new', the UI must display a badge labeled 'New Request' or 'Pending Processing'. The 'Confirm' action in the admin UI should include a tooltip: 'This booking has already reserved the time slot; Confirming marks your internal review as complete
•	Conflict UX: Simulate concurrent bookings → FE receives 409 and displays conflict modal (owner: FE uses BE conflict response).
•	Performance & Lighthouse checks pass in CI (owner: FE).
Deliverables (FE)
•	repo/frontend/README.md with dev/run/build/test instructions.
•	Staging & production URLs.
•	Component library repo/frontend/src/components.
•	Test report repo/frontend/tests/report.html.
•	Quick manual repo/handover/manual.pdf.





	
