import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router";
import { adminLogin } from "../../lib/api";
import { setToken } from "../../lib/auth";

export default function AdminLogin() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await adminLogin(email, password);
      const token = res?.token || res?.data?.token;
      if (!token) throw new Error("Missing token");
      setToken(token);
      const target = (location.state as any)?.from || "/admin";
      navigate(target);
    } catch (err: any) {
      setError(err?.message || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-stone-50 flex items-center justify-center px-4">
      <form
        onSubmit={onSubmit}
        className="w-full max-w-md bg-white p-8 rounded-xl border border-stone-200 shadow-sm"
      >
        <div className="text-right mb-6">
          <a href="/admin/forgot-password" className="text-sm text-[#c83d26] hover:underline">
            Forgot password?
          </a>
        </div>

        <h1 className="text-2xl font-bold text-stone-900 mb-4">Admin Login</h1>
        {error && <p className="text-red-600 text-sm mb-3">{error}</p>}

        <label className="text-sm font-semibold text-stone-700">Email</label>
        <input
          className="w-full mt-1 mb-4 px-3 py-2 border border-stone-300 rounded"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <label className="text-sm font-semibold text-stone-700">Password</label>
        <input
          type="password"
          className="w-full mt-1 mb-6 px-3 py-2 border border-stone-300 rounded"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button
          type="submit"
          disabled={loading}
          className="w-full py-2 bg-[#c83d26] text-white rounded font-semibold"
        >
          {loading ? "Signing in..." : "Sign In"}
        </button>
      </form>
    </div>
  );
}
