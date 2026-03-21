import React, { useEffect, useState } from "react";
import { FaqDTO, createAdminFaq, fetchAdminFaqs } from "../../lib/api";

export default function AdminFaqs() {
  const [items, setItems] = useState<FaqDTO[]>([]);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [published, setPublished] = useState(false);

  useEffect(() => {
    fetchAdminFaqs()
      .then((rows) => setItems(Array.isArray(rows) ? rows : []))
      .catch(() => setItems([]));
  }, []);

  const add = async (e: React.FormEvent) => {
    e.preventDefault();
    const created = await createAdminFaq({
      question: question.trim(),
      answer: answer.trim(),
      published
    });
    setItems((prev) => [created, ...prev]);
    setQuestion("");
    setAnswer("");
    setPublished(false);
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-stone-900 mb-4">FAQs</h1>

      <form onSubmit={add} className="bg-white border border-stone-200 rounded-xl p-4 mb-6 space-y-3">
        <input
          className="w-full border px-3 py-2 rounded"
          placeholder="Question"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          required
        />
        <textarea
          className="w-full border px-3 py-2 rounded"
          placeholder="Answer"
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          required
        />
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={published} onChange={(e) => setPublished(e.target.checked)} />
          Published
        </label>
        <button className="bg-[#c83d26] text-white px-4 py-2 rounded">Add FAQ</button>
      </form>

      <div className="bg-white border border-stone-200 rounded-xl p-4 space-y-4">
        {items.length === 0 && <p className="text-sm text-stone-500">No FAQs yet.</p>}
        {items.map((faq) => (
          <div key={faq.id} className="border-b border-stone-200 pb-3">
            <p className="text-stone-900 font-medium">{faq.question}</p>
            <p className="text-stone-600 text-sm mt-1">{faq.answer}</p>
            <p className="text-xs text-stone-500 mt-1">{faq.published ? "Published" : "Draft"}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
