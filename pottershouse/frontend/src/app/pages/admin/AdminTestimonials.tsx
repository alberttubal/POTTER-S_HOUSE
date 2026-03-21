import React, { useEffect, useState } from "react";
import {
  TestimonialDTO,
  createAdminTestimonial,
  fetchAdminTestimonials
} from "../../lib/api";

export default function AdminTestimonials() {
  const [items, setItems] = useState<TestimonialDTO[]>([]);
  const [customerName, setCustomerName] = useState("");
  const [content, setContent] = useState("");
  const [published, setPublished] = useState(false);

  useEffect(() => {
    fetchAdminTestimonials()
      .then((res) => setItems(Array.isArray(res) ? res : []))
      .catch(() => setItems([]));
  }, []);

  const add = async (e: React.FormEvent) => {
    e.preventDefault();
    const created = await createAdminTestimonial({
      customer_name: customerName.trim(),
      content: content.trim(),
      published
    });
    setItems((prev) => [created, ...prev]);
    setCustomerName("");
    setContent("");
    setPublished(false);
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-stone-900 mb-4">Testimonials</h1>
      <form onSubmit={add} className="bg-white border border-stone-200 rounded-xl p-4 mb-6 space-y-3">
        <input className="w-full border px-3 py-2 rounded" placeholder="Customer Name" value={customerName} onChange={(e) => setCustomerName(e.target.value)} required />
        <textarea className="w-full border px-3 py-2 rounded" placeholder="Content" value={content} onChange={(e) => setContent(e.target.value)} required />
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={published} onChange={(e) => setPublished(e.target.checked)} />
          Published
        </label>
        <button className="bg-[#c83d26] text-white px-4 py-2 rounded">Add</button>
      </form>

      <div className="bg-white border border-stone-200 rounded-xl p-4">
        {items.length === 0 && <p className="text-sm text-stone-500">No testimonials yet.</p>}
        {items.map((t) => (
          <div key={t.id} className="border-b border-stone-200 py-3">
            <p className="text-stone-900 font-medium">{t.customer_name}</p>
            <p className="text-stone-600 text-sm">{t.content}</p>
            <p className="text-xs text-stone-500">{t.published ? "Published" : "Draft"}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
