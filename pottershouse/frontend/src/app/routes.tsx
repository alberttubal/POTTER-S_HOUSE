import React, { lazy } from "react";
import { createBrowserRouter } from "react-router";
import Layout from "./components/Layout";
import AdminShell from "./pages/admin/AdminShell";
import AdminLogin from "./pages/admin/AdminLogin";

const Home = lazy(() => import("./pages/Home"));
const Packages = lazy(() => import("./pages/Packages"));
const PackageDetail = lazy(() => import("./pages/PackageDetail"));
const Gallery = lazy(() => import("./pages/Gallery"));
const Faqs = lazy(() => import("./pages/Faqs"));
const Contact = lazy(() => import("./pages/Contact"));
const Health = lazy(() => import("./pages/Health"));

const AdminDashboard = lazy(() => import("./pages/admin/AdminDashboard"));
const AdminBookings = lazy(() => import("./pages/admin/AdminBookings"));
const AdminBookingDetail = lazy(() => import("./pages/admin/AdminBookingDetail"));
const AdminPackages = lazy(() => import("./pages/admin/AdminPackages"));
const AdminUploads = lazy(() => import("./pages/admin/AdminUploads"));
const AdminTestimonials = lazy(() => import("./pages/admin/AdminTestimonials"));
const AdminFaqs = lazy(() => import("./pages/admin/AdminFaqs"));
const AdminSettings = lazy(() => import("./pages/admin/AdminSettings"));
const AdminForgotPassword = lazy(() => import("./pages/admin/AdminForgotPassword"));
const AdminResetPassword = lazy(() => import("./pages/admin/AdminResetPassword"));

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Layout,
    children: [
      { index: true, Component: Home },
      { path: "packages", Component: Packages },
      { path: "packages/:id", Component: PackageDetail },
      { path: "gallery", Component: Gallery },
      { path: "faqs", Component: Faqs },
      { path: "contact", Component: Contact },
      { path: "health-ui", Component: Health }
    ]
  },
  {
    path: "admin",
    children: [
      { path: "login", Component: AdminLogin },
      { path: "forgot-password", Component: AdminForgotPassword },
      { path: "reset-password", Component: AdminResetPassword },
      {
        Component: AdminShell,
        children: [
          { index: true, Component: AdminDashboard },
          { path: "bookings", Component: AdminBookings },
          { path: "bookings/:id", Component: AdminBookingDetail },
          { path: "packages", Component: AdminPackages },
          { path: "uploads", Component: AdminUploads },
          { path: "testimonials", Component: AdminTestimonials },
          { path: "faqs", Component: AdminFaqs },
          { path: "settings", Component: AdminSettings }
        ]
      }
    ]
  }
]);
