import React from "react";
import { Navigate, Outlet, useLocation } from "react-router";
import { isAuthed } from "../../lib/auth";
import AdminLayout from "./AdminLayout";

const PUBLIC_ADMIN_PATHS = new Set([
  "/admin/login",
  "/admin/forgot-password",
  "/admin/reset-password"
]);

export default function AdminShell() {
  const location = useLocation();

  if (PUBLIC_ADMIN_PATHS.has(location.pathname)) {
    return <Outlet />;
  }

  if (!isAuthed()) {
    return <Navigate to="/admin/login" replace state={{ from: location.pathname }} />;
  }

  return (
    <AdminLayout>
      <Outlet />
    </AdminLayout>
  );
}
