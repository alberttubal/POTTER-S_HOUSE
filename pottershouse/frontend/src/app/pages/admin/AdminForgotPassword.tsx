import React, { useState } from "react";
import { Link } from "react-router";
import { ApiError, adminPasswordForgot } from "../../lib/api";

function getErrorMessage(error: unknown) {
  if (error instanceof ApiError) return error.message;
  if (error instanceof Error) return error.message;
  return "Unable to send reset link. Please try again.";
}

export default function AdminForgotPassword() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage("");
    setError("");
    setLoading(true);

    try {
      await adminPasswordForgot(email.trim());
      setMessage("If the email exists, a reset link has been sent.");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-stone-50 flex items-center justify-center px-4">
      <form onSubmit={onSubmit} className="w-full max-w-md bg-white p-8 rounded-xl border border-stone-200 shadow-sm">
        <h1 className="text-2xl font-bold text-stone-900 mb-4">Forgot Password</h1>

        {error && <p className="text-sm text-red-600 mb-3">{error}</p>}
        {message && <p className="text-sm text-stone-600 mb-3">{message}</p>}

        <input
          className="w-full mt-1 mb-4 px-3 py-2 border border-stone-300 rounded"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          placeholder="admin@example.com"
        />

        <button
          className="w-full py-2 bg-[#c83d26] text-white rounded font-semibold disabled:opacity-70"
          disabled={loading}
        >
          {loading ? "Sending..." : "Send Reset Link"}
        </button>

        <Link to="/admin/login" className="text-sm text-[#c83d26] mt-4 inline-block">
          Back to login
        </Link>
      </form>
    </div>
  );
}
