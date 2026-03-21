import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router";
import { ArrowRight, Star, CalendarCheck, Utensils, Heart } from "lucide-react";
import {
  PackageDTO,
  TestimonialDTO,
  fetchPublicPackages,
  fetchPublicTestimonials
} from "../lib/api";

const PACKAGE_FALLBACK_IMAGES = [
  "https://images.unsplash.com/photo-1661994215679-cde7c2c5c060?auto=format&fit=crop&w=1200&q=80",
  "https://images.unsplash.com/photo-1767324672816-e09a2a0a3979?auto=format&fit=crop&w=1200&q=80",
  "https://images.unsplash.com/photo-1609834265242-75d58b7db409?auto=format&fit=crop&w=1200&q=80"
];

function formatPrice(value: string) {
  const numberValue = Number(value);
  if (Number.isNaN(numberValue)) return value;
  return numberValue.toLocaleString("en-PH", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  });
}

export default function Home() {
  const [featuredPackages, setFeaturedPackages] = useState<PackageDTO[]>([]);
  const [testimonials, setTestimonials] = useState<TestimonialDTO[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    Promise.all([fetchPublicPackages(1, 3, true), fetchPublicTestimonials()])
      .then(([packagesRes, testimonialsRes]) => {
        if (!mounted) return;
        setFeaturedPackages(Array.isArray(packagesRes.results) ? packagesRes.results.slice(0, 3) : []);
        setTestimonials(Array.isArray(testimonialsRes) ? testimonialsRes : []);
      })
      .catch(() => {
        if (!mounted) return;
        setFeaturedPackages([]);
        setTestimonials([]);
      })
      .finally(() => {
        if (!mounted) return;
        setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  const featureCards = useMemo(
    () => [
      {
        name: "Exceptional Taste",
        description: "Our dishes are prepared with fresh ingredients and authentic recipes.",
        icon: <Utensils className="w-6 h-6 text-[#c83d26]" />
      },
      {
        name: "Tailored Packages",
        description: "We offer flexible menu options to fit your event and budget.",
        icon: <Heart className="w-6 h-6 text-[#c83d26]" />
      },
      {
        name: "Reliable Service",
        description: "Punctual setup and professional service for a smooth event.",
        icon: <CalendarCheck className="w-6 h-6 text-[#c83d26]" />
      }
    ],
    []
  );

  const featuredTestimonial = testimonials[0] || null;

  return (
    <div>
      <section className="relative bg-stone-900 overflow-hidden">
        <div className="absolute inset-0">
          <img
            src="https://images.unsplash.com/photo-1537495988501-f9cd94a78f3e?auto=format&fit=crop&w=1600&q=80"
            alt="Potter's House catering hero"
            className="w-full h-full object-cover opacity-40"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-stone-900 via-stone-900/40 to-transparent"></div>
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 lg:py-32 flex flex-col items-center text-center">
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold text-white tracking-tight mb-6 drop-shadow-md">
            Unforgettable Flavors for <br className="hidden md:block" />
            <span className="text-[#c83d26]">Your Special Moments</span>
          </h1>
          <p className="mt-4 text-xl text-stone-200 max-w-2xl mx-auto mb-10 drop-shadow">
            Premium catering service for intimate gatherings and grand celebrations.
          </p>
          <div className="flex flex-col sm:flex-row gap-4">
            <Link
              to="/packages"
              className="px-8 py-3.5 border border-transparent text-base font-semibold rounded-md text-white bg-[#c83d26] hover:bg-[#a83320] transition-colors shadow-lg shadow-red-900/20 flex items-center justify-center gap-2"
            >
              View Packages <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              to="/contact"
              className="px-8 py-3.5 border-2 border-white text-base font-semibold rounded-md text-white bg-transparent hover:bg-white/10 transition-colors flex items-center justify-center"
            >
              Book Now
            </Link>
          </div>
        </div>
      </section>

      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-stone-900 uppercase tracking-tight">Featured Buffet Packages</h2>
            <div className="w-24 h-1 bg-[#c83d26] mx-auto mt-4 rounded-full"></div>
            <p className="mt-4 text-stone-600 max-w-2xl mx-auto">
              These packages come directly from your backend package management.
            </p>
          </div>

          {loading && <p className="text-center text-stone-500">Loading featured packages...</p>}

          {!loading && featuredPackages.length === 0 && (
            <p className="text-center text-stone-500">No active packages available right now.</p>
          )}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {featuredPackages.map((pkg, index) => (
              <div key={pkg.id} className="bg-[#faf8f5] rounded-xl overflow-hidden shadow-sm border border-stone-100 hover:shadow-md transition-shadow group">
                <div className="h-48 overflow-hidden relative">
                  <img
                    src={PACKAGE_FALLBACK_IMAGES[index % PACKAGE_FALLBACK_IMAGES.length]}
                    alt={pkg.name}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute top-4 right-4 bg-white/90 backdrop-blur px-3 py-1 rounded-full text-sm font-bold text-[#c83d26]">
                    P{formatPrice(pkg.price)}/pax
                  </div>
                </div>
                <div className="p-6">
                  <h3 className="text-xl font-bold text-stone-900 mb-2">{pkg.name}</h3>
                  <p className="text-stone-600 mb-4 text-sm line-clamp-3">
                    {pkg.description?.trim() || "Package details are available on the package page."}
                  </p>
                  <Link to={`/packages/${pkg.id}`} className="text-[#c83d26] font-medium flex items-center gap-1 hover:gap-2 transition-all">
                    View package <ArrowRight className="w-4 h-4" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 bg-stone-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-stone-900 uppercase tracking-tight mb-6">Why Choose Potter's House?</h2>
              <p className="text-stone-600 mb-8 text-lg">
                We combine quality food, responsive coordination, and dependable event service.
              </p>
              <div className="space-y-6">
                {featureCards.map((feature) => (
                  <div key={feature.name} className="flex gap-4">
                    <div className="flex-shrink-0 mt-1">
                      <div className="w-12 h-12 bg-red-50 rounded-lg flex items-center justify-center">
                        {feature.icon}
                      </div>
                    </div>
                    <div>
                      <h4 className="text-lg font-bold text-stone-900">{feature.name}</h4>
                      <p className="mt-1 text-stone-600">{feature.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <img src="https://images.unsplash.com/photo-1654579920979-8ebb4e96b755?auto=format&fit=crop&w=900&q=80" alt="Beef dish" className="rounded-lg w-full h-64 object-cover shadow-md" />
              <img src="https://images.unsplash.com/photo-1679279726940-be5ce80c632c?auto=format&fit=crop&w=900&q=80" alt="Pancit dish" className="rounded-lg w-full h-64 object-cover shadow-md mt-8" />
            </div>
          </div>
        </div>
      </section>

      <section className="py-20 bg-stone-900 text-white text-center">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <Star className="w-12 h-12 text-yellow-400 mx-auto mb-6 opacity-80" />

          {featuredTestimonial ? (
            <>
              <h2 className="text-2xl md:text-3xl font-medium leading-relaxed italic text-stone-200 mb-8">
                "{featuredTestimonial.content}"
              </h2>
              <div className="flex items-center justify-center gap-3">
                <div className="w-10 h-10 bg-stone-700 rounded-full flex items-center justify-center font-bold">
                  {featuredTestimonial.customer_name.slice(0, 2).toUpperCase()}
                </div>
                <div className="text-left">
                  <p className="font-bold">{featuredTestimonial.customer_name}</p>
                  <p className="text-sm text-stone-400">Verified Client</p>
                </div>
              </div>
            </>
          ) : (
            <h2 className="text-xl text-stone-300">
              Customer testimonials will appear here once published from admin.
            </h2>
          )}
        </div>
      </section>
    </div>
  );
}
