import React, { useState } from "react";
import { Link, useSearchParams } from "react-router";
import { ApiError, adminPasswordReset } from "../../lib/api";

function getErrorMessage(error: unknown) {
  if (error instanceof ApiError) return error.message;
  if (error instanceof Error) return error.message;
  return "Unable to reset password. Please try again.";
}

export default function AdminResetPassword() {
  const [params] = useSearchParams();
  const uid = params.get("uid") || "";
  const token = params.get("token") || "";

  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const hasResetParams = Boolean(uid && token);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage("");
    setError("");

    if (!hasResetParams) {
      setError("Invalid or missing reset link parameters.");
      return;
    }

    setLoading(true);
    try {
      await adminPasswordReset(uid, token, password);
      setMessage("Password reset successful. You can now login.");
      setPassword("");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-stone-50 flex items-center justify-center px-4">
      <form onSubmit={onSubmit} className="w-full max-w-md bg-white p-8 rounded-xl border border-stone-200 shadow-sm">
        <h1 className="text-2xl font-bold text-stone-900 mb-4">Reset Password</h1>

        {!hasResetParams && (
          <p className="text-sm text-red-600 mb-3">Invalid reset link. Please request a new one.</p>
        )}
        {error && <p className="text-sm text-red-600 mb-3">{error}</p>}
        {message && <p className="text-sm text-stone-600 mb-3">{message}</p>}

        <input
          type="password"
          className="w-full mt-1 mb-4 px-3 py-2 border border-stone-300 rounded"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={8}
          placeholder="New password"
        />

        <button
          className="w-full py-2 bg-[#c83d26] text-white rounded font-semibold disabled:opacity-70"
          disabled={loading || !hasResetParams}
        >
          {loading ? "Resetting..." : "Reset Password"}
        </button>

        <Link to="/admin/login" className="text-sm text-[#c83d26] mt-4 inline-block">
          Back to login
        </Link>
      </form>
    </div>
  );
}
