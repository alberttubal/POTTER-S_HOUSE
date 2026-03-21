import React, { useEffect, useMemo, useState } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { Calendar, Users, Phone, Facebook, MessageSquare, Loader2, MapPin } from "lucide-react";
import { useSearchParams } from "react-router";
import {
  ApiError,
  BookingPayload,
  PackageDTO,
  SettingDTO,
  createBooking,
  fetchPublicPackages,
  fetchPublicSettings,
  unwrapResults
} from "../lib/api";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from "../components/ui/dialog";

type BookingFormData = {
  customer_name: string;
  phone: string;
  email: string;
  event_type: string;
  event_date_start: string;
  event_date_end: string;
  event_all_day: boolean;
  guests: number;
  package_id?: string;
  notes?: string;
  dietary_needs?: string;
  honeypot: string;
};

type ConflictBooking = {
  id: string;
  event_date_start: string;
  event_date_end: string;
};

type SuggestedAlternative = {
  event_date_start: string;
  event_date_end: string;
};

type ApiErrorDetail = {
  field?: string;
  message?: string | string[];
};


const OWNER_WHATSAPP_E164 = "639065055942";
const MANILA_TZ = "Asia/Manila";
const MANILA_UTC_OFFSET_HOURS = 8;

function parseLocal(localInput: string) {
  const match = localInput.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})$/);
  if (!match) return null;

  const year = Number(match[1]);
  const month = Number(match[2]);
  const day = Number(match[3]);
  const hour = Number(match[4]);
  const minute = Number(match[5]);

  if (month < 1 || month > 12) return null;
  if (hour < 0 || hour > 23) return null;
  if (minute < 0 || minute > 59) return null;

  const maxDay = new Date(Date.UTC(year, month, 0)).getUTCDate();
  if (day < 1 || day > maxDay) return null;

  const utcMs = Date.UTC(year, month - 1, day, hour - MANILA_UTC_OFFSET_HOURS, minute, 0, 0);
  const value = new Date(utcMs);
  return Number.isNaN(value.getTime()) ? null : value;
}

function toIso(localInput: string) {
  const value = parseLocal(localInput);
  return value ? value.toISOString() : "";
}

function formatDateTime(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return new Intl.DateTimeFormat("en-PH", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: MANILA_TZ
  }).format(date);
}


function flattenMessage(message: string | string[] | undefined) {
  if (Array.isArray(message)) {
    return message.join(", ");
  }
  return message || "Invalid value";
}

function createIdempotencyKey() {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return `booking-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

function normalizeSettingValue(value: unknown) {
  if (typeof value === "string") return value;
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  return "";
}

function settingsToMap(rows: SettingDTO[]) {
  const map: Record<string, string> = {};
  rows.forEach((row) => {
    const value = normalizeSettingValue(row.value).trim();
    if (value) {
      map[row.key] = value;
    }
  });
  return map;
}

function firstSetting(map: Record<string, string>, keys: string[]) {
  for (const key of keys) {
    const value = (map[key] || "").trim();
    if (value) return value;
  }
  return "";
}

export default function Contact() {
  const [searchParams] = useSearchParams();
  const preSelectedPackage = searchParams.get("package") || "";

  const [packages, setPackages] = useState<PackageDTO[]>([]);
  const [settingsMap, setSettingsMap] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [retryAfter, setRetryAfter] = useState<number | null>(null);
  const [successData, setSuccessData] = useState<{ bookingId: string } | null>(null);
  const [conflictData, setConflictData] = useState<{
    conflicts: ConflictBooking[];
    alternatives: SuggestedAlternative[];
  } | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    setError
  } = useForm<BookingFormData>({
    defaultValues: {
      package_id: preSelectedPackage,
      guests: 50,
      event_all_day: false,
      honeypot: ""
    }
  });

  useEffect(() => {
    let mounted = true;
    fetchPublicPackages(1, 100, true)
      .then((res) => {
        if (!mounted) return;
        setPackages(unwrapResults<PackageDTO>(res));
      })
      .catch(() => {
        if (!mounted) return;
        setPackages([]);
      });
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    let mounted = true;
    fetchPublicSettings()
      .then((rows) => {
        if (!mounted) return;
        setSettingsMap(settingsToMap(Array.isArray(rows) ? rows : []));
      })
      .catch(() => {
        if (!mounted) return;
        setSettingsMap({});
      });
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    if (retryAfter === null) return;
    if (retryAfter <= 0) {
      setRetryAfter(null);
      return;
    }
    const timer = setTimeout(() => {
      setRetryAfter((value) => (value === null ? null : Math.max(0, value - 1)));
    }, 1000);
    return () => clearTimeout(timer);
  }, [retryAfter]);

  const packageOptions = useMemo(
    () =>
      packages.map((pkg) => ({
        id: pkg.id,
        label: `${pkg.name} (P${pkg.price}/pax)`
      })),
    [packages]
  );

  const onSubmit = async (data: BookingFormData) => {
    if (data.honeypot) return;

    const start = parseLocal(data.event_date_start);
    const end = parseLocal(data.event_date_end);

    if (!start) {
      setError("event_date_start", { message: "Invalid start date and time" });
      return;
    }
    if (!end) {
      setError("event_date_end", { message: "Invalid end date and time" });
      return;
    }
    if (start.getTime() < Date.now()) {
      setError("event_date_start", { message: "Start date must be in the future" });
      return;
    }
    if (end.getTime() < start.getTime()) {
      setError("event_date_end", { message: "End date must be after start date" });
      return;
    }

    const payload: BookingPayload = {
      customer_name: data.customer_name.trim(),
      phone: data.phone.trim(),
      email: data.email.trim(),
      event_type: data.event_type,
      event_date_start: toIso(data.event_date_start),
      event_date_end: toIso(data.event_date_end),
      event_all_day: Boolean(data.event_all_day),
      guests: Number(data.guests),
      package_id: data.package_id || null,
      notes: data.notes?.trim() || "",
      dietary_needs: data.dietary_needs?.trim() || "",
      honeypot: ""
    };

    setIsSubmitting(true);
    setConflictData(null);

    try {
      const result = await createBooking(payload, createIdempotencyKey());
      const response = (result || {}) as { id?: string; bookingId?: string; data?: { bookingId?: string } };
      const bookingId = response.id || response.bookingId || response.data?.bookingId || "Pending";
      setSuccessData({ bookingId });
      toast.success("Booking request submitted", {
        description: "We will contact you shortly to confirm details."
      });
      reset({
        package_id: preSelectedPackage,
        guests: 50,
        event_all_day: false,
        honeypot: ""
      });
    } catch (error) {
      if (!(error instanceof ApiError)) {
        toast.error("Server error. Please try again.");
        return;
      }

      const payloadData = (error.data || {}) as {
        retryAfter?: number | string;
        error?: {
          details?: ApiErrorDetail[];
          conflictingBookings?: ConflictBooking[];
          suggested_alternatives?: SuggestedAlternative[];
        };
      };

      if (error.status === 409) {
        setConflictData({
          conflicts: payloadData.error?.conflictingBookings || [],
          alternatives: payloadData.error?.suggested_alternatives || []
        });
        toast.error("Selected schedule conflicts with an existing booking.");
        return;
      }

      if (error.status === 429) {
        const retry = Number(payloadData.retryAfter || 30);
        setRetryAfter(Number.isNaN(retry) ? 30 : retry);
        toast.error(`Too many requests. Try again in ${Number.isNaN(retry) ? 30 : retry} seconds.`);
        return;
      }

      const details = payloadData.error?.details || [];
      details.forEach((detail) => {
        if (!detail.field) return;
        const field = detail.field as keyof BookingFormData;
        setError(field, { message: flattenMessage(detail.message) });
      });
      toast.error(error.message || "Failed to submit booking.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const phonePrimary = firstSetting(settingsMap, ["contact_phone_primary", "contact_phone"]);
  const phoneSecondary = firstSetting(settingsMap, ["contact_phone_secondary"]);
  const phoneLines = [phonePrimary, phoneSecondary].filter(Boolean);
  const facebookUrl = firstSetting(settingsMap, ["facebook_url"]);
  const businessAddress = firstSetting(settingsMap, ["business_address"]);
  const whatsappDigits = firstSetting(settingsMap, ["whatsapp_number"]).replace(/\D/g, "");

  const whatsappLink = successData && whatsappDigits
    ? `https://wa.me/${whatsappDigits}?text=${encodeURIComponent(
        `Hi! I submitted a booking request. Ref: ${successData.bookingId}`
      )}`
    : "";

  return (
    <div className="py-12 bg-stone-50 min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-extrabold text-stone-900 tracking-tight uppercase mb-4">Contact & Booking</h1>
          <p className="text-lg text-stone-600 max-w-2xl mx-auto">
            Ready to plan your event? Fill out the form below or reach out to us directly.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
          <div className="lg:col-span-1 space-y-8">
            <div className="bg-white rounded-2xl shadow-sm border border-stone-200 p-8">
              <h3 className="text-xl font-bold text-stone-900 mb-6 uppercase tracking-wide border-b border-stone-100 pb-4">Get In Touch</h3>
              <div className="space-y-6">
                <div className="flex items-start gap-4">
                  <div className="bg-red-50 p-3 rounded-full text-[#c83d26]">
                    <Phone className="w-5 h-5" />
                  </div>
                  <div>
                    <p className="font-semibold text-stone-900">Phone</p>
                    {phoneLines.length > 0 ? (
                      phoneLines.map((line) => (
                        <p key={line} className="text-stone-600 mt-1">{line}</p>
                      ))
                    ) : (
                      <p className="text-stone-500 mt-1 text-sm">Set contact_phone in admin settings.</p>
                    )}
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="bg-red-50 p-3 rounded-full text-[#c83d26]">
                    <MapPin className="w-5 h-5" />
                  </div>
                  <div>
                    <p className="font-semibold text-stone-900">Address</p>
                    <p className="text-stone-600 mt-1">
                      {businessAddress || "Set business_address in admin settings."}
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="bg-red-50 p-3 rounded-full text-[#c83d26]">
                    <Facebook className="w-5 h-5" />
                  </div>
                  <div>
                    <p className="font-semibold text-stone-900">Facebook</p>
                    {facebookUrl ? (
                      <a href={facebookUrl} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline mt-1 block">
                        Visit Facebook Page
                      </a>
                    ) : (
                      <p className="text-stone-500 mt-1 text-sm">Set facebook_url in admin settings.</p>
                    )}
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="bg-red-50 p-3 rounded-full text-[#c83d26]">
                    <MessageSquare className="w-5 h-5" />
                  </div>
                  <div>
                    <p className="font-semibold text-stone-900">We Deliver!</p>
                    <p className="text-stone-600 mt-1 text-sm">Contact us to arrange delivery for your packed meals or catering setups.</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-[#c83d26] rounded-2xl shadow-md p-8 text-white relative overflow-hidden">
              <div className="absolute -right-8 -top-8 text-red-900/30">
                <Calendar className="w-48 h-48" />
              </div>
              <div className="relative z-10">
                <h3 className="text-xl font-bold mb-2">Notice</h3>
                <p className="text-red-100 mb-4">Please book at least 1 week in advance for large events to ensure availability and proper preparation.</p>
              </div>
            </div>
          </div>

          <div className="lg:col-span-2">
            <div className="bg-white rounded-2xl shadow-sm border border-stone-200 p-8">
              <h3 className="text-2xl font-bold text-stone-900 mb-8 uppercase tracking-tight">Request a Quote</h3>

              <form id="booking-form" onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                <div className="hidden">
                  <label htmlFor="honeypot">Website</label>
                  <input id="honeypot" {...register("honeypot")} autoComplete="off" tabIndex={-1} />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label htmlFor="customer_name" className="text-sm font-semibold text-stone-700">Full Name *</label>
                    <input
                      id="customer_name"
                      {...register("customer_name", { required: "Name is required" })}
                      className="w-full px-4 py-3 rounded-lg border border-stone-300 focus:ring-2 focus:ring-[#c83d26] focus:border-[#c83d26] outline-none transition-shadow"
                      placeholder="Juan Dela Cruz"
                    />
                    {errors.customer_name && <p className="text-red-500 text-xs mt-1">{errors.customer_name.message}</p>}
                  </div>

                  <div className="space-y-2">
                    <label htmlFor="phone" className="text-sm font-semibold text-stone-700">Phone Number *</label>
                    <input
                      id="phone"
                      {...register("phone", {
                        required: "Phone is required",
                        pattern: { value: /^\+?[0-9()\s-]{7,20}$/i, message: "Invalid phone number" }
                      })}
                      className="w-full px-4 py-3 rounded-lg border border-stone-300 focus:ring-2 focus:ring-[#c83d26] focus:border-[#c83d26] outline-none transition-shadow"
                      placeholder="0912 345 6789"
                    />
                    {errors.phone && <p className="text-red-500 text-xs mt-1">{errors.phone.message}</p>}
                  </div>

                  <div className="space-y-2">
                    <label htmlFor="email" className="text-sm font-semibold text-stone-700">Email Address *</label>
                    <input
                      id="email"
                      type="email"
                      {...register("email", {
                        required: "Email is required",
                        pattern: { value: /^\S+@\S+$/i, message: "Invalid email" }
                      })}
                      className="w-full px-4 py-3 rounded-lg border border-stone-300 focus:ring-2 focus:ring-[#c83d26] focus:border-[#c83d26] outline-none transition-shadow"
                      placeholder="juan@example.com"
                    />
                    {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email.message}</p>}
                  </div>

                  <div className="space-y-2">
                    <label htmlFor="event_type" className="text-sm font-semibold text-stone-700">Event Type *</label>
                    <select
                      id="event_type"
                      {...register("event_type", { required: "Event type is required" })}
                      className="w-full px-4 py-3 rounded-lg border border-stone-300 focus:ring-2 focus:ring-[#c83d26] focus:border-[#c83d26] outline-none transition-shadow bg-white"
                    >
                      <option value="">Select an event type...</option>
                      <option value="wedding">Wedding</option>
                      <option value="birthday">Birthday / Debut</option>
                      <option value="corporate">Corporate Event</option>
                      <option value="anniversary">Anniversary</option>
                      <option value="other">Other</option>
                    </select>
                    {errors.event_type && <p className="text-red-500 text-xs mt-1">{errors.event_type.message}</p>}
                  </div>

                  <div className="space-y-2">
                    <label htmlFor="event_date_start" className="text-sm font-semibold text-stone-700">Event Date & Time (Asia/Manila) *</label>
                    <input
                      id="event_date_start"
                      type="datetime-local"
                      {...register("event_date_start", { required: "Start date is required" })}
                      className="w-full px-4 py-3 rounded-lg border border-stone-300 focus:ring-2 focus:ring-[#c83d26] focus:border-[#c83d26] outline-none transition-shadow"
                    />
                    {errors.event_date_start && <p className="text-red-500 text-xs mt-1">{errors.event_date_start.message}</p>}
                  </div>

                  <div className="space-y-2">
                    <label htmlFor="event_date_end" className="text-sm font-semibold text-stone-700">End Date & Time (Asia/Manila) *</label>
                    <input
                      id="event_date_end"
                      type="datetime-local"
                      {...register("event_date_end", { required: "End time is required" })}
                      className="w-full px-4 py-3 rounded-lg border border-stone-300 focus:ring-2 focus:ring-[#c83d26] focus:border-[#c83d26] outline-none transition-shadow"
                    />
                    {errors.event_date_end && <p className="text-red-500 text-xs mt-1">{errors.event_date_end.message}</p>}
                  </div>

                  <div className="space-y-2">
                    <label htmlFor="event_all_day" className="text-sm font-semibold text-stone-700">All Day Event</label>
                    <div className="flex items-center gap-3">
                      <input id="event_all_day" type="checkbox" {...register("event_all_day")} />
                      <span className="text-sm text-stone-600">Yes, this is an all-day event</span>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label htmlFor="guests" className="text-sm font-semibold text-stone-700">Number of Guests *</label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <Users className="h-5 w-5 text-stone-400" />
                      </div>
                      <input
                        id="guests"
                        type="number"
                        min="1"
                        {...register("guests", {
                          required: "Guest count is required",
                          min: { value: 1, message: "Guests must be at least 1" },
                          valueAsNumber: true
                        })}
                        className="w-full pl-10 pr-4 py-3 rounded-lg border border-stone-300 focus:ring-2 focus:ring-[#c83d26] focus:border-[#c83d26] outline-none transition-shadow"
                      />
                    </div>
                    {errors.guests && <p className="text-red-500 text-xs mt-1">{errors.guests.message}</p>}
                  </div>

                  <div className="space-y-2">
                    <label htmlFor="package_id" className="text-sm font-semibold text-stone-700">Preferred Package</label>
                    <select
                      id="package_id"
                      {...register("package_id")}
                      className="w-full px-4 py-3 rounded-lg border border-stone-300 focus:ring-2 focus:ring-[#c83d26] focus:border-[#c83d26] outline-none transition-shadow bg-white"
                    >
                      <option value="">I'm not sure yet / Custom</option>
                      {packageOptions.map((pkg) => (
                        <option key={pkg.id} value={pkg.id}>
                          {pkg.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="space-y-2">
                  <label htmlFor="dietary_needs" className="text-sm font-semibold text-stone-700">Dietary Needs</label>
                  <input
                    id="dietary_needs"
                    {...register("dietary_needs")}
                    className="w-full px-4 py-3 rounded-lg border border-stone-300 focus:ring-2 focus:ring-[#c83d26] focus:border-[#c83d26] outline-none transition-shadow"
                    placeholder="E.g., halal, vegetarian, no peanuts"
                  />
                </div>

                <div className="space-y-2">
                  <label htmlFor="notes" className="text-sm font-semibold text-stone-700">Additional Notes</label>
                  <textarea
                    id="notes"
                    {...register("notes")}
                    rows={4}
                    className="w-full px-4 py-3 rounded-lg border border-stone-300 focus:ring-2 focus:ring-[#c83d26] focus:border-[#c83d26] outline-none transition-shadow resize-none"
                    placeholder="Event address, special instructions, etc."
                  />
                </div>

                <button
                  type="submit"
                  disabled={isSubmitting || retryAfter !== null}
                  className="w-full bg-[#c83d26] text-white py-4 rounded-lg font-bold text-lg hover:bg-[#a83320] transition-colors disabled:opacity-70 disabled:cursor-not-allowed flex justify-center items-center"
                >
                  {isSubmitting ? (
                    <>
                      <Loader2 className="w-6 h-6 animate-spin mr-2" /> Submitting Request...
                    </>
                  ) : retryAfter !== null ? (
                    `Try again in ${retryAfter}s`
                  ) : (
                    "Submit Booking Request"
                  )}
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>

      <Dialog open={Boolean(successData)} onOpenChange={(open) => !open && setSuccessData(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Booking Submitted</DialogTitle>
            <DialogDescription>
              Your request has been submitted. Save your reference number below.
            </DialogDescription>
          </DialogHeader>
          <div className="text-sm text-stone-700">
            Reference: <span className="font-semibold">{successData?.bookingId}</span>
          </div>
          <DialogFooter>
            {whatsappLink ? (
              <a
                href={whatsappLink}
                target="_blank"
                rel="noreferrer"
                className="px-4 py-2 bg-[#c83d26] text-white rounded-lg text-sm font-semibold"
              >
                Message on WhatsApp
              </a>
            ) : (
              <button
                type="button"
                disabled
                className="px-4 py-2 bg-stone-300 text-stone-600 rounded-lg text-sm font-semibold"
              >
                WhatsApp not configured
              </button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={Boolean(conflictData)} onOpenChange={(open) => !open && setConflictData(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Time Conflict</DialogTitle>
            <DialogDescription>
              The selected time conflicts with existing bookings. Please choose another slot.
            </DialogDescription>
          </DialogHeader>
          <div className="text-sm text-stone-700 space-y-4">
            <div>
              <p className="font-semibold">Conflicting bookings</p>
              <ul className="list-disc ml-5">
                {(conflictData?.conflicts || []).map((conflict) => (
                  <li key={conflict.id}>
                    {formatDateTime(conflict.event_date_start)} to {formatDateTime(conflict.event_date_end)}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <p className="font-semibold">Suggested alternatives</p>
              <ul className="list-disc ml-5">
                {(conflictData?.alternatives || []).map((alternative, index) => (
                  <li key={`${alternative.event_date_start}-${index}`}>
                    {formatDateTime(alternative.event_date_start)} to {formatDateTime(alternative.event_date_end)}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
