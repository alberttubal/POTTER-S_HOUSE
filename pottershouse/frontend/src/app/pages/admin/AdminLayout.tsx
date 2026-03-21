import React from "react";
import { NavLink, useNavigate } from "react-router";
import { LayoutDashboard, CalendarDays, Upload, Users, Settings, LogOut, Package, CircleHelp } from "lucide-react";
import { clearToken } from "../../lib/auth";

const navItems = [
  { to: "/admin", label: "Dashboard", icon: LayoutDashboard },
  { to: "/admin/bookings", label: "Bookings", icon: CalendarDays },
  { to: "/admin/packages", label: "Packages", icon: Package },
  { to: "/admin/uploads", label: "Uploads", icon: Upload },
  { to: "/admin/testimonials", label: "Testimonials", icon: Users },
  { to: "/admin/faqs", label: "FAQs", icon: CircleHelp },
  { to: "/admin/settings", label: "Settings", icon: Settings }
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate();

  const logout = () => {
    clearToken();
    navigate("/admin/login");
  };

  return (
    <div className="min-h-screen bg-stone-100 flex">
      <aside className="w-64 bg-stone-900 text-white hidden md:flex flex-col">
        <div className="p-6 border-b border-stone-800">
          <h2 className="text-xl font-bold uppercase tracking-widest text-[#c83d26]">Admin Portal</h2>
        </div>
        <nav className="flex-1 p-4 space-y-2">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-colors ${
                  isActive ? "bg-[#c83d26] text-white" : "text-stone-300 hover:bg-stone-800"
                }`
              }
            >
              <item.icon className="w-5 h-5" />
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="p-4 border-t border-stone-800">
          <button
            onClick={logout}
            className="flex items-center gap-3 px-4 py-3 text-stone-300 hover:text-white transition-colors"
          >
            <LogOut className="w-5 h-5" /> Logout
          </button>
        </div>
      </aside>

      <main className="flex-1 p-6 md:p-8">{children}</main>
    </div>
  );
}
