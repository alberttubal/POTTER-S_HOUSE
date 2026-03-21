import React, { useEffect, useState } from "react";
import { UploadDTO, fetchPublicGallery } from "../lib/api";

function resolveGalleryUrl(url: string) {
  if (!url || typeof window === "undefined") {
    return url;
  }

  try {
    const parsed = new URL(url);
    if (parsed.hostname === "minio") {
      parsed.hostname = window.location.hostname;
      parsed.port = "9000";
      parsed.protocol = window.location.protocol === "https:" ? "https:" : "http:";
      return parsed.toString();
    }
    return parsed.toString();
  } catch {
    return url;
  }
}

export default function Gallery() {
  const [images, setImages] = useState<UploadDTO[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;
    fetchPublicGallery()
      .then((res) => {
        if (!mounted) return;
        setImages(Array.isArray(res) ? res : []);
      })
      .catch(() => {
        if (!mounted) return;
        setImages([]);
        setError("Unable to load gallery right now.");
      })
      .finally(() => {
        if (!mounted) return;
        setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className="py-12 bg-stone-50 min-h-screen">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-extrabold text-stone-900 tracking-tight uppercase mb-4">Event Gallery</h1>
          <p className="text-lg text-stone-600 max-w-2xl mx-auto">
            A glimpse into the delicious setups and events catered by Potter&apos;s House.
          </p>
        </div>

        {loading && <p className="text-center text-stone-600">Loading gallery...</p>}
        {!loading && error && <p className="text-center text-red-600">{error}</p>}
        {!loading && !error && images.length === 0 && (
          <p className="text-center text-stone-600">No published gallery images yet.</p>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 auto-rows-[250px]">
          {images.map((image, index) => (
            <div
              key={image.id}
              className={`rounded-xl overflow-hidden shadow-sm group relative ${
                index === 0 ? "md:col-span-2 md:row-span-2" : index === 3 ? "md:col-span-2" : ""
              }`}
            >
              <img
                src={resolveGalleryUrl(image.url)}
                alt={image.alt_text || `Gallery image ${index + 1}`}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 ease-in-out"
                loading="lazy"
              />
              <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
                <div className="w-12 h-12 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
                  </svg>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
