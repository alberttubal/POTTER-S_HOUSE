import React, { useEffect, useState } from "react";
import { Link } from "react-router";
import { BookingDTO, fetchAdminBookings } from "../../lib/api";

const PAGE_SIZE = 20;

function formatDate(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("en-PH", {
    dateStyle: "medium",
    timeStyle: "short"
  });
}

function readableWorkflow(status: BookingDTO["workflow_status"]) {
  if (status === "new") return "New Request";
  if (status === "contacted") return "Contacted";
  if (status === "confirmed") return "Internally Confirmed";
  if (status === "paid") return "Paid";
  if (status === "completed") return "Completed";
  if (status === "cancelled") return "Cancelled";
  return status;
}

export default function AdminBookings() {
  const [bookings, setBookings] = useState<BookingDTO[]>([]);
  const [statusFilter, setStatusFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    fetchAdminBookings({
      page,
      pageSize: PAGE_SIZE,
      status: statusFilter === "all" ? undefined : statusFilter,
      q: searchQuery.trim() || undefined
    })
      .then((res) => {
        if (!mounted) return;
        setBookings(Array.isArray(res.results) ? res.results : []);
        setTotalCount(typeof res.count === "number" ? res.count : 0);
      })
      .catch(() => {
        if (!mounted) return;
        setBookings([]);
        setTotalCount(0);
      })
      .finally(() => {
        if (!mounted) return;
        setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, [page, searchQuery, statusFilter]);

  const totalPages = Math.max(1, Math.ceil(totalCount / PAGE_SIZE));

  return (
    <div>
      <div className="flex flex-col gap-3 mb-6 md:flex-row md:items-center md:justify-between">
        <h1 className="text-2xl font-bold text-stone-900">Bookings</h1>
        <div className="flex flex-col gap-2 md:flex-row">
          <input
            value={searchQuery}
            onChange={(event) => {
              setPage(1);
              setSearchQuery(event.target.value);
            }}
            placeholder="Search name, phone, email"
            className="border border-stone-300 rounded px-3 py-2 text-sm"
          />
          <select
            className="border border-stone-300 rounded px-3 py-2 text-sm"
            value={statusFilter}
            onChange={(event) => {
              setPage(1);
              setStatusFilter(event.target.value);
            }}
          >
            <option value="all">All</option>
            <option value="new">New</option>
            <option value="contacted">Contacted</option>
            <option value="confirmed">Confirmed</option>
            <option value="paid">Paid</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-stone-200 overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-stone-50 text-stone-500 text-xs uppercase tracking-wider">
            <tr>
              <th className="px-6 py-3 font-medium">Ref ID</th>
              <th className="px-6 py-3 font-medium">Client</th>
              <th className="px-6 py-3 font-medium">Event Date</th>
              <th className="px-6 py-3 font-medium">Guests</th>
              <th className="px-6 py-3 font-medium">Workflow</th>
              <th className="px-6 py-3 font-medium">Booking Status</th>
              <th className="px-6 py-3 font-medium text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-stone-200">
            {bookings.map((booking) => (
              <tr key={booking.id} className="hover:bg-stone-50">
                <td className="px-6 py-4 text-sm font-medium">{booking.id.slice(0, 8)}...</td>
                <td className="px-6 py-4 text-sm">{booking.customer_name}</td>
                <td className="px-6 py-4 text-sm">{formatDate(booking.event_date_start)}</td>
                <td className="px-6 py-4 text-sm">{booking.guests}</td>
                <td className="px-6 py-4 text-sm">{readableWorkflow(booking.workflow_status)}</td>
                <td className="px-6 py-4 text-sm capitalize">{booking.status}</td>
                <td className="px-6 py-4 text-sm text-right">
                  <Link to={`/admin/bookings/${booking.id}`} className="text-[#c83d26] font-medium hover:underline">
                    Review
                  </Link>
                </td>
              </tr>
            ))}
            {!loading && bookings.length === 0 && (
              <tr>
                <td colSpan={7} className="px-6 py-6 text-center text-sm text-stone-500">
                  No bookings found.
                </td>
              </tr>
            )}
            {loading && (
              <tr>
                <td colSpan={7} className="px-6 py-6 text-center text-sm text-stone-500">
                  Loading bookings...
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between mt-4 text-sm text-stone-600">
        <div>
          Page {Math.min(page, totalPages)} of {totalPages}
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setPage((value) => Math.max(1, value - 1))}
            disabled={page <= 1}
            className="px-3 py-1 rounded border border-stone-300 disabled:opacity-50"
          >
            Prev
          </button>
          <button
            onClick={() => setPage((value) => Math.min(totalPages, value + 1))}
            disabled={page >= totalPages}
            className="px-3 py-1 rounded border border-stone-300 disabled:opacity-50"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}
