import React, { useEffect, useState } from "react";
import { BookingDTO, fetchAdminBookings } from "../../lib/api";

function toReadableStatus(status: BookingDTO["workflow_status"]) {
  switch (status) {
    case "new":
      return "New Request";
    case "contacted":
      return "Contacted";
    case "confirmed":
      return "Internally Confirmed";
    case "paid":
      return "Paid";
    case "completed":
      return "Completed";
    case "cancelled":
      return "Cancelled";
    default:
      return status;
  }
}

function formatDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("en-PH", {
    dateStyle: "medium",
    timeStyle: "short"
  });
}

export default function AdminDashboard() {
  const [totalBookings, setTotalBookings] = useState(0);
  const [newBookings, setNewBookings] = useState(0);
  const [recentBookings, setRecentBookings] = useState<BookingDTO[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;

    Promise.all([
      fetchAdminBookings({ page: 1, pageSize: 1 }),
      fetchAdminBookings({ page: 1, pageSize: 1, status: "new" }),
      fetchAdminBookings({ page: 1, pageSize: 5 })
    ])
      .then(([allRes, newRes, recentRes]) => {
        if (!mounted) return;
        setTotalBookings(typeof allRes.count === "number" ? allRes.count : 0);
        setNewBookings(typeof newRes.count === "number" ? newRes.count : 0);
        setRecentBookings(Array.isArray(recentRes.results) ? recentRes.results : []);
      })
      .catch(() => {
        if (!mounted) return;
        setTotalBookings(0);
        setNewBookings(0);
        setRecentBookings([]);
      })
      .finally(() => {
        if (!mounted) return;
        setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div>
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-stone-900">Dashboard Overview</h1>
          <p className="text-stone-500 text-sm">Welcome back, Admin</p>
        </div>
        <div className="bg-white px-4 py-2 rounded-lg shadow-sm border border-stone-200 text-sm font-medium text-stone-600">
          Today: <span className="text-stone-900">{new Date().toLocaleDateString("en-PH")}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-stone-200">
          <h3 className="text-stone-500 text-sm font-medium mb-1">Total Bookings</h3>
          <p className="text-3xl font-bold text-stone-900">{loading ? "..." : totalBookings}</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-stone-200">
          <h3 className="text-stone-500 text-sm font-medium mb-1">New Requests</h3>
          <p className="text-3xl font-bold text-amber-500">{loading ? "..." : newBookings}</p>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-stone-200">
          <h3 className="text-stone-500 text-sm font-medium mb-1">Revenue (MTD)</h3>
          <p className="text-3xl font-bold text-stone-900">P0</p>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-stone-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-stone-200 bg-stone-50">
          <h2 className="text-lg font-bold text-stone-900">Recent Booking Requests</h2>
        </div>
        <div className="p-6 text-sm text-stone-600">
          {recentBookings.length === 0 && !loading && "No bookings yet."}
          {loading && "Loading bookings..."}
          {recentBookings.length > 0 && (
            <div className="space-y-3">
              {recentBookings.map((booking) => (
                <div key={booking.id} className="border border-stone-200 rounded-lg px-4 py-3">
                  <div className="font-medium text-stone-900">{booking.customer_name}</div>
                  <div className="text-stone-600">{formatDate(booking.event_date_start)}</div>
                  <div className="text-xs text-stone-500">{toReadableStatus(booking.workflow_status)}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
