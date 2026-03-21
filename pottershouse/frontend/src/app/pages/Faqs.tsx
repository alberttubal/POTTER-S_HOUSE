import React, { useEffect, useState } from "react";
import { FaqDTO, fetchPublicFaqs } from "../lib/api";

export default function Faqs() {
  const [items, setItems] = useState<FaqDTO[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;
    fetchPublicFaqs()
      .then((rows) => {
        if (!mounted) return;
        setItems(Array.isArray(rows) ? rows : []);
      })
      .catch(() => {
        if (!mounted) return;
        setItems([]);
        setError("Unable to load FAQs right now.");
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
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-4xl font-extrabold text-stone-900 tracking-tight uppercase mb-4">Frequently Asked Questions</h1>
        <p className="text-stone-600 mb-10">Answers are managed from the admin FAQ module.</p>

        {loading && <p className="text-stone-600">Loading FAQs...</p>}
        {!loading && error && <p className="text-red-600">{error}</p>}
        {!loading && !error && items.length === 0 && <p className="text-stone-600">No FAQs published yet.</p>}

        <div className="space-y-4">
          {items.map((faq) => (
            <div key={faq.id} className="bg-white border border-stone-200 rounded-xl p-5">
              <h2 className="text-lg font-bold text-stone-900">{faq.question}</h2>
              <p className="text-stone-700 mt-2 whitespace-pre-line">{faq.answer}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
