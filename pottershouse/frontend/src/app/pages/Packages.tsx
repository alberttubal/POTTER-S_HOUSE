import React, { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router";
import { Info } from "lucide-react";
import { PackageDTO, fetchPublicPackages } from "../lib/api";

export default function Packages() {
  const [activeTab, setActiveTab] = useState<"buffet" | "alacarte" | "packed">("buffet");
  const [searchParams, setSearchParams] = useSearchParams();
  const [items, setItems] = useState<PackageDTO[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [loadError, setLoadError] = useState("");

  const page = Math.max(1, Number(searchParams.get("page") || "1"));
  const pageSize = Math.max(1, Number(searchParams.get("pageSize") || "12"));
  const totalPages = Math.max(1, Math.ceil(totalCount / pageSize));

  useEffect(() => {
    if (activeTab !== "buffet") return;
    setLoading(true);
    setLoadError("");
    fetchPublicPackages(page, pageSize, true)
      .then((res) => {
        setItems(Array.isArray(res.results) ? res.results : []);
        setTotalCount(typeof res.count === "number" ? res.count : 0);
      })
      .catch(() => {
        setItems([]);
        setTotalCount(0);
        setLoadError("Unable to load buffet packages right now.");
      })
      .finally(() => setLoading(false));
  }, [activeTab, page, pageSize]);

  const updatePage = (nextPage: number) => {
    const bounded = Math.max(1, nextPage);
    const params = new URLSearchParams(searchParams);
    params.set("page", String(bounded));
    params.set("pageSize", String(pageSize));
    setSearchParams(params);
  };

  const alaCarteCategories = [
    {
      name: "Beef",
      items: [
        { name: "Beef w/ Mushroom", price: "1200.00" },
        { name: "Beef Steak", price: "1000.00" },
        { name: "Beef Stew", price: "1200.00" },
        { name: "Kare-Kare", price: "1500.00" },
        { name: "Beef w/ Ampalaya", price: "1100.00" },
        { name: "Beef w/ Brocolli", price: "1200.00" }
      ]
    },
    {
      name: "Chicken",
      items: [
        { name: "Battered Chicken", price: "850.00" },
        { name: "Chicken Afritada", price: "900.00" },
        { name: "Chicken Curry", price: "900.00" },
        { name: "Chili Wings", price: "900.00" },
        { name: "Chicken 'n' Mushroom", price: "1000.00" },
        { name: "Chicken Cordon blu", price: "1000.00" }
      ]
    },
    {
      name: "Pork",
      items: [
        { name: "Bola-Bola", price: "900.00" },
        { name: "Breaded Porkchop", price: "900.00" },
        { name: "Hamonada", price: "1200.00" },
        { name: "Lumpia Shanghai", price: "900.00" },
        { name: "Pork Afritada", price: "1200.00" },
        { name: "Pork Steak", price: "1200.00" },
        { name: "Sweet 'n' Sour Pork", price: "1200.00" },
        { name: "Humba", price: "1200.00" },
        { name: "Patatim", price: "1300.00" }
      ]
    },
    {
      name: "Seafoods",
      items: [
        { name: "Kinilaw", price: "1300.00" },
        { name: "Sinuglaw", price: "1500.00" },
        { name: "Sweet 'n' Sour (Dowry)", price: "850.00" },
        { name: "Sweet 'n' Sour Tuna", price: "1000.00" },
        { name: "Lapu-Lapu (L)", price: "1400.00" },
        { name: "Mixed Seafoods in Cajun Sauce", price: "1500.00" }
      ]
    }
  ];

  const packedMeals = [
    { price: "150.00", items: ["Sotanghon", "Battered Chicken", "Rice"] },
    { price: "165.00", items: ["Spaghetti", "Battered Chicken"] },
    { price: "150.00", items: ["Beef Steak", "Cassava/Maja/Brownies", "Bam-I", "Rice"] },
    { price: "250.00", items: ["Beef Steak", "Chicken", "Four Seasons", "Dessert", "Rice"] }
  ];

  return (
    <div className="py-12 bg-stone-50 min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-extrabold text-stone-900 tracking-tight uppercase mb-4">Our Menus</h1>
          <p className="text-lg text-stone-600 max-w-2xl mx-auto">
            Explore our wide range of catering options, from comprehensive buffet packages to customized a la carte selections.
          </p>
        </div>

        <div className="flex justify-center mb-12">
          <div className="bg-white p-1 rounded-xl shadow-sm inline-flex border border-stone-200">
            {(["buffet", "alacarte", "packed"] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-6 py-2.5 rounded-lg text-sm font-semibold capitalize transition-all ${
                  activeTab === tab
                    ? "bg-[#c83d26] text-white shadow-sm"
                    : "text-stone-600 hover:bg-stone-50 hover:text-stone-900"
                }`}
              >
                {tab === "alacarte" ? "A La Carte" : tab === "packed" ? "Packed Meals & Lechon" : "Buffet Packages"}
              </button>
            ))}
          </div>
        </div>

        {activeTab === "buffet" && (
          <div className="space-y-10">
            <div className="flex justify-between items-center text-sm text-stone-600">
              <span>Page {Math.min(page, totalPages)} of {totalPages}</span>
              <div className="flex gap-2">
                <button
                  onClick={() => updatePage(Math.max(1, page - 1))}
                  disabled={page <= 1}
                  className="px-3 py-1 rounded border border-stone-200 disabled:opacity-50"
                >
                  Prev
                </button>
                <button
                  onClick={() => updatePage(Math.min(totalPages, page + 1))}
                  disabled={page >= totalPages}
                  className="px-3 py-1 rounded border border-stone-200 disabled:opacity-50"
                >
                  Next
                </button>
              </div>
            </div>

            {loading && <div className="text-sm text-stone-600">Loading packages...</div>}
            {loadError && <div className="text-sm text-red-600">{loadError}</div>}

            {!loading && !loadError && items.length === 0 && (
              <div className="text-sm text-stone-600">No active buffet packages available.</div>
            )}

            {items.map((pkg) => (
              <div key={pkg.id} className="bg-white rounded-2xl shadow-sm border border-stone-200 overflow-hidden flex flex-col md:flex-row">
                <div className="bg-[#c83d26] text-white p-8 md:w-1/3 flex flex-col justify-center text-center border-b md:border-b-0 md:border-r border-red-800">
                  <h2 className="text-2xl font-bold uppercase tracking-wide mb-2">{pkg.name}</h2>
                  <div className="text-5xl font-extrabold mb-2 flex items-center justify-center">
                    <span className="text-2xl font-normal mr-1">P</span>
                    {pkg.price}
                  </div>
                  <p className="text-red-100 font-medium tracking-wider text-sm uppercase">per pax</p>
                  <Link
                    to={`/packages/${pkg.id}`}
                    className="mt-6 px-6 py-3 bg-white text-[#c83d26] font-bold rounded-lg shadow-md hover:bg-red-50 transition-colors"
                  >
                    View Details
                  </Link>
                  <Link
                    to={`/contact?package=${pkg.id}`}
                    className="mt-3 px-6 py-3 bg-black/20 text-white font-bold rounded-lg hover:bg-black/30 transition-colors"
                  >
                    Book This Package
                  </Link>
                </div>

                <div className="p-8 md:w-2/3 space-y-4">
                  <h3 className="text-lg font-bold text-stone-900">Package Description</h3>
                  <p className="text-stone-700 text-sm leading-6">
                    {pkg.description?.trim() || "Package details will be finalized during booking confirmation."}
                  </p>
                  <div className="flex items-start text-xs text-stone-600 bg-stone-100 p-3 rounded-lg text-left">
                    <Info className="w-4 h-4 mr-2 flex-shrink-0 mt-0.5" />
                    <span>Final menu combinations can be customized with our team.</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === "alacarte" && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {alaCarteCategories.map((category, idx) => (
              <div key={idx} className="bg-white rounded-xl shadow-sm border border-stone-200 overflow-hidden">
                <div className="bg-stone-900 px-6 py-4">
                  <h3 className="text-lg font-bold text-white uppercase tracking-wider">{category.name}</h3>
                </div>
                <div className="p-0">
                  <ul className="divide-y divide-stone-100">
                    {category.items.map((item, iIdx) => (
                      <li key={iIdx} className="px-6 py-3 flex justify-between items-center hover:bg-stone-50 transition-colors">
                        <span className="text-stone-800 font-medium text-sm">{item.name}</span>
                        <span className="text-[#c83d26] font-bold text-sm">P{item.price}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === "packed" && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-white rounded-2xl shadow-sm border border-stone-200 overflow-hidden">
              <div className="bg-stone-900 px-8 py-5">
                <h3 className="text-xl font-bold text-white uppercase tracking-wider">Packed Meals</h3>
                <p className="text-stone-400 text-sm mt-1">Minimum of 30 pax</p>
              </div>
              <div className="p-8 grid grid-cols-1 sm:grid-cols-2 gap-6">
                {packedMeals.map((meal, idx) => (
                  <div key={idx} className="bg-stone-50 rounded-xl p-5 border border-stone-100">
                    <div className="text-xl font-bold text-[#c83d26] mb-3 border-b border-stone-200 pb-2">
                      Php {meal.price}
                    </div>
                    <ul className="space-y-1.5 text-sm text-stone-700 font-medium">
                      {meal.items.map((item, iIdx) => (
                        <li key={iIdx}>• {item}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
              <div className="bg-stone-100 px-8 py-4 text-xs text-stone-600 flex flex-wrap gap-4 border-t border-stone-200">
                <span className="font-semibold text-stone-900">Add-ons:</span>
                <span>Tetra juice - P15.00</span>
                <span>Water - P15.00</span>
                <span>Coke - P25.00</span>
              </div>
            </div>

            <div className="bg-white rounded-2xl shadow-sm border border-stone-200 overflow-hidden flex flex-col">
              <div className="bg-[#c83d26] px-8 py-5">
                <h3 className="text-xl font-bold text-white uppercase tracking-wider">Whole Lechon</h3>
                <p className="text-red-100 text-sm mt-1">The centerpiece of every celebration</p>
              </div>
              <div className="p-8 flex-grow">
                <ul className="space-y-4">
                  <li className="flex justify-between items-center p-4 bg-stone-50 rounded-lg border border-stone-100">
                    <div>
                      <span className="block font-bold text-stone-900 text-lg">De Leche</span>
                      <span className="text-xs text-stone-500 uppercase tracking-wide">20-25 pax</span>
                    </div>
                    <span className="text-lg font-bold text-[#c83d26]">P7,000.00</span>
                  </li>
                  <li className="flex justify-between items-center p-4 bg-stone-50 rounded-lg border border-stone-100">
                    <div>
                      <span className="block font-bold text-stone-900 text-lg">Medium</span>
                      <span className="text-xs text-stone-500 uppercase tracking-wide">35-40 pax</span>
                    </div>
                    <span className="text-lg font-bold text-[#c83d26]">P9,000.00</span>
                  </li>
                  <li className="flex justify-between items-center p-4 bg-stone-50 rounded-lg border border-stone-100">
                    <div>
                      <span className="block font-bold text-stone-900 text-lg">Large</span>
                      <span className="text-xs text-stone-500 uppercase tracking-wide">40-45 pax</span>
                    </div>
                    <span className="text-lg font-bold text-[#c83d26]">P10,000.00</span>
                  </li>
                  <li className="flex justify-between items-center p-4 bg-stone-50 rounded-lg border border-stone-100 shadow-sm border-[#c83d26]/30 relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-12 h-12 bg-[#c83d26]/10 rounded-bl-full"></div>
                    <div>
                      <span className="block font-bold text-stone-900 text-lg">XL</span>
                      <span className="text-xs text-stone-500 uppercase tracking-wide">50-60 pax</span>
                    </div>
                    <span className="text-lg font-bold text-[#c83d26]">P15,000.00</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
