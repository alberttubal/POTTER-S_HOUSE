import React, { useEffect, useState } from "react";
import { useParams } from "react-router";
import { ApiError, BookingDTO, fetchAdminBooking, updateAdminBooking } from "../../lib/api";

function formatDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("en-PH", {
    dateStyle: "medium",
    timeStyle: "short"
  });
}

function workflowLabel(status: BookingDTO["workflow_status"]) {
  if (status === "new") return "New Request";
  if (status === "contacted") return "Contacted";
  if (status === "confirmed") return "Internally Confirmed";
  if (status === "paid") return "Paid";
  if (status === "completed") return "Completed";
  if (status === "cancelled") return "Cancelled";
  return status;
}

export default function AdminBookingDetail() {
  const { id } = useParams();
  const [booking, setBooking] = useState<BookingDTO | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) {
      setLoading(false);
      setBooking(null);
      return;
    }

    setLoading(true);
    setError("");
    fetchAdminBooking(id)
      .then((res) => {
        setBooking(res);
      })
      .catch(() => {
        setBooking(null);
        setError("Booking not found or failed to load.");
      })
      .finally(() => {
        setLoading(false);
      });
  }, [id]);

  const markConfirmed = async () => {
    if (!id || !booking) return;
    setSaving(true);
    setMessage("");
    setError("");
    try {
      const updated = await updateAdminBooking(id, { workflow_status: "confirmed" });
      setBooking(updated);
      setMessage("Workflow updated to confirmed.");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message || "Failed to update booking.");
      } else {
        setError("Failed to update booking.");
      }
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <div className="text-stone-600">Loading booking...</div>;
  }

  if (!booking) {
    return <div className="text-stone-600">{error || "Booking not found."}</div>;
  }

  const confirmDisabled =
    saving || booking.workflow_status === "confirmed" || booking.workflow_status === "cancelled";

  return (
    <div>
      <h1 className="text-2xl font-bold text-stone-900 mb-4">Booking Detail</h1>
      <div className="bg-white border border-stone-200 rounded-xl p-6 space-y-3 text-sm">
        <div><strong>Reference:</strong> {booking.id}</div>
        <div><strong>Name:</strong> {booking.customer_name}</div>
        <div><strong>Phone:</strong> {booking.phone}</div>
        <div><strong>Email:</strong> {booking.email}</div>
        <div><strong>Event type:</strong> {booking.event_type}</div>
        <div><strong>Event:</strong> {formatDate(booking.event_date_start)} to {formatDate(booking.event_date_end)}</div>
        <div><strong>All day:</strong> {booking.event_all_day ? "Yes" : "No"}</div>
        <div><strong>Guests:</strong> {booking.guests}</div>
        <div><strong>Package ID:</strong> {booking.package_id || "-"}</div>
        <div><strong>Workflow:</strong> {workflowLabel(booking.workflow_status)}</div>
        <div><strong>Booking status:</strong> {booking.status}</div>
        <div><strong>Dietary needs:</strong> {booking.dietary_needs || "-"}</div>
        <div><strong>Notes:</strong> {booking.notes || "-"}</div>
      </div>

      <button
        onClick={markConfirmed}
        disabled={confirmDisabled}
        title="Public bookings already reserve the slot. This action confirms your internal workflow review."
        className="mt-6 px-4 py-2 bg-[#c83d26] text-white rounded disabled:opacity-60"
      >
        {saving ? "Updating..." : "Mark Workflow as Confirmed"}
      </button>

      {message && <p className="mt-3 text-sm text-green-700">{message}</p>}
      {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
    </div>
  );
}
