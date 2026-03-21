import React from "react";
import { Outlet, Link, useLocation } from "react-router";
import { UtensilsCrossed, Menu, X, Facebook, Phone, MapPin } from "lucide-react";
import { fetchPublicSettings, SettingDTO } from "../lib/api";

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

export default function Layout() {
  const [isMenuOpen, setIsMenuOpen] = React.useState(false);
  const [settingsMap, setSettingsMap] = React.useState<Record<string, string>>({});
  const location = useLocation();

  React.useEffect(() => {
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

  const phonePrimary = firstSetting(settingsMap, ["contact_phone_primary", "contact_phone"]);
  const phoneSecondary = firstSetting(settingsMap, ["contact_phone_secondary"]);
  const phoneLines = [phonePrimary, phoneSecondary].filter(Boolean);
  const facebookUrl = firstSetting(settingsMap, ["facebook_url"]);
  const businessAddress = firstSetting(settingsMap, ["business_address"]);

  const navLinks = [
    { name: "Home", path: "/" },
    { name: "Packages", path: "/packages" },
    { name: "Gallery", path: "/gallery" },
    { name: "FAQs", path: "/faqs" },
    { name: "Contact & Booking", path: "/contact" },
  ];

  return (
    <div className="min-h-screen bg-[#faf8f5] flex flex-col font-sans text-stone-800">
      <header className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            <div className="flex-shrink-0 flex items-center">
              <Link to="/" className="flex items-center gap-2 text-[#c83d26]">
                <div className="bg-[#c83d26] p-2 rounded-full text-white">
                  <UtensilsCrossed className="w-6 h-6" />
                </div>
                <div className="flex flex-col">
                  <span className="font-bold text-xl leading-none tracking-tight uppercase">Potter's House</span>
                  <span className="text-xs font-medium tracking-widest text-stone-500 uppercase">Catering Services</span>
                </div>
              </Link>
            </div>

            <nav className="hidden md:flex space-x-8">
              {navLinks.map((link) => (
                <Link
                  key={link.name}
                  to={link.path}
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors ${
                    location.pathname === link.path
                      ? "border-[#c83d26] text-[#c83d26]"
                      : "border-transparent text-stone-500 hover:text-stone-700 hover:border-stone-300"
                  }`}
                >
                  {link.name}
                </Link>
              ))}
              <Link
                to="/admin"
                className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-[#c83d26] bg-red-50 hover:bg-red-100 transition-colors"
              >
                Admin
              </Link>
            </nav>

            <div className="flex items-center md:hidden">
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                aria-label={isMenuOpen ? "Close menu" : "Open menu"}
                aria-expanded={isMenuOpen}
                aria-controls="mobile-nav"
                className="inline-flex items-center justify-center p-2 rounded-md text-stone-400 hover:text-stone-500 hover:bg-stone-100 focus:outline-none"
              >
                {isMenuOpen ? <X className="block h-6 w-6" /> : <Menu className="block h-6 w-6" />}
              </button>
            </div>
          </div>
        </div>

        {isMenuOpen && (
          <div id="mobile-nav" className="md:hidden bg-white border-t border-stone-100">
            <div className="pt-2 pb-3 space-y-1">
              {navLinks.map((link) => (
                <Link
                  key={link.name}
                  to={link.path}
                  onClick={() => setIsMenuOpen(false)}
                  className={`block pl-3 pr-4 py-2 border-l-4 text-base font-medium ${
                    location.pathname === link.path
                      ? "bg-red-50 border-[#c83d26] text-[#c83d26]"
                      : "border-transparent text-stone-500 hover:bg-stone-50 hover:text-stone-700"
                  }`}
                >
                  {link.name}
                </Link>
              ))}
              <Link
                to="/admin"
                onClick={() => setIsMenuOpen(false)}
                className="block pl-3 pr-4 py-2 border-l-4 border-transparent text-base font-medium text-stone-500 hover:bg-stone-50 hover:text-stone-700"
              >
                Admin Portal
              </Link>
            </div>
          </div>
        )}
      </header>

      <main className="flex-grow">
        <Outlet />
      </main>

      <footer className="bg-stone-900 text-stone-300 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <div className="flex items-center gap-2 text-white mb-4">
              <div className="bg-[#c83d26] p-1.5 rounded-full">
                <UtensilsCrossed className="w-5 h-5" />
              </div>
              <span className="font-bold text-lg uppercase tracking-tight">Potter's House</span>
            </div>
            <p className="text-sm text-stone-400 max-w-xs">
              Providing excellent catering services for all your special occasions. We deliver quality food and service.
            </p>
          </div>

          <div>
            <h3 className="text-white font-semibold mb-4 uppercase text-sm tracking-wider">Contact Us</h3>
            <ul className="space-y-3 text-sm">
              <li className="flex items-start gap-2">
                <Phone className="w-4 h-4 text-[#c83d26] mt-0.5" />
                <span>
                  {phoneLines.length > 0 ? phoneLines.join(" / ") : "Set contact_phone in admin settings."}
                </span>
              </li>
              <li className="flex items-start gap-2">
                <MapPin className="w-4 h-4 text-[#c83d26] mt-0.5" />
                <span>{businessAddress || "Set business_address in admin settings."}</span>
              </li>
              <li className="flex items-start gap-2">
                <Facebook className="w-4 h-4 text-[#c83d26] mt-0.5" />
                {facebookUrl ? (
                  <a href={facebookUrl} target="_blank" rel="noreferrer" className="hover:text-white transition-colors">
                    Visit Facebook Page
                  </a>
                ) : (
                  <span>Set facebook_url in admin settings.</span>
                )}
              </li>
            </ul>
          </div>

          <div>
            <h3 className="text-white font-semibold mb-4 uppercase text-sm tracking-wider">Quick Links</h3>
            <ul className="space-y-2 text-sm">
              <li><Link to="/packages" className="hover:text-[#c83d26] transition-colors">Our Menus</Link></li>
              <li><Link to="/faqs" className="hover:text-[#c83d26] transition-colors">FAQs</Link></li>
              <li><Link to="/contact" className="hover:text-[#c83d26] transition-colors">Book an Event</Link></li>
              <li><Link to="/gallery" className="hover:text-[#c83d26] transition-colors">Event Gallery</Link></li>
            </ul>
          </div>
        </div>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-12 pt-8 border-t border-stone-800 text-xs text-stone-500 flex flex-col md:flex-row justify-between items-center">
          <p>&copy; {new Date().getFullYear()} Potter's House Catering Services. All rights reserved.</p>
          <p className="mt-2 md:mt-0">Design based on required spec.</p>
        </div>
      </footer>
    </div>
  );
}
