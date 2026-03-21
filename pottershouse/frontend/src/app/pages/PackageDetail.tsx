import React, { useEffect, useState } from "react";
import { Link, useParams } from "react-router";
import { PackageDTO, fetchPublicPackage } from "../lib/api";

const PLACEHOLDER_IMAGE =
  "https://images.unsplash.com/photo-1555244162-803834f70033?auto=format&fit=crop&w=1400&q=80";

export default function PackageDetail() {
  const { id } = useParams();
  const [pkg, setPkg] = useState<PackageDTO | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) {
      setPkg(null);
      setError("Package not found.");
      setLoading(false);
      return;
    }

    setLoading(true);
    setError("");
    fetchPublicPackage(id)
      .then((res) => {
        setPkg(res);
      })
      .catch(() => {
        setPkg(null);
        setError("Package not found.");
      })
      .finally(() => {
        setLoading(false);
      });
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-stone-50 py-16">
        <div className="max-w-3xl mx-auto px-4 text-center text-stone-600">Loading package details...</div>
      </div>
    );
  }

  if (!pkg) {
    return (
      <div className="min-h-screen bg-stone-50 py-16">
        <div className="max-w-3xl mx-auto px-4 text-center">
          <h1 className="text-3xl font-bold text-stone-900">Package Not Found</h1>
          <p className="text-stone-600 mt-2">{error || "Please return to the packages list."}</p>
          <Link to="/packages" className="inline-block mt-6 text-[#c83d26] font-semibold">
            Back to Packages
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-stone-50 py-12">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 items-start">
          <div className="bg-white rounded-2xl border border-stone-200 shadow-sm p-4">
            <img
              src={PLACEHOLDER_IMAGE}
              alt={`${pkg.name} package`}
              className="w-full h-[360px] object-cover rounded-xl"
            />
          </div>

          <div>
            <h1 className="text-4xl font-extrabold text-stone-900">{pkg.name}</h1>
            <p className="text-stone-600 mt-2">
              {pkg.description?.trim() || "Package details will be finalized during your booking confirmation."}
            </p>
            <div className="mt-6 flex items-center gap-4">
              <span className="text-3xl font-bold text-[#c83d26]">P{pkg.price}</span>
              <span className="text-sm text-stone-500">per pax</span>
            </div>
            <div className="mt-4 text-sm text-stone-600 bg-stone-100 px-4 py-3 rounded-lg">
              Availability and exact menu set are confirmed by the team after booking review.
            </div>
            <div className="mt-6 flex gap-3">
              <Link
                to={`/contact?package=${pkg.id}#booking-form`}
                className="px-6 py-3 bg-[#c83d26] text-white rounded-lg font-semibold"
              >
                Request Quote / Book
              </Link>
              <Link
                to="/packages"
                className="px-6 py-3 border border-stone-300 rounded-lg font-semibold text-stone-700"
              >
                Back to Packages
              </Link>
            </div>
          </div>
        </div>

        <div className="mt-10 bg-white rounded-xl border border-stone-200 p-6">
          <h3 className="text-lg font-bold text-stone-900 mb-3">Notes</h3>
          <ul className="space-y-2 text-sm text-stone-700">
            <li>• Price shown is per guest and subject to final event requirements.</li>
            <li>• Event date remains tentative until admin confirms schedule and details.</li>
            <li>• Add-on services and setup requirements are discussed during final quotation.</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
