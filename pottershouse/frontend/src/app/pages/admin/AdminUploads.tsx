import React, { useEffect, useState } from "react";
import {
  UploadDTO,
  fetchAdminUploadsList,
  updateAdminUpload,
  uploadImages
} from "../../lib/api";

export default function AdminUploads() {
  const [files, setFiles] = useState<File[]>([]);
  const [items, setItems] = useState<UploadDTO[]>([]);
  const [message, setMessage] = useState("");

  const load = async () => {
    const list = await fetchAdminUploadsList();
    setItems(Array.isArray(list) ? list : []);
  };

  useEffect(() => {
    load().catch(() => setItems([]));
  }, []);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage("");
    if (!files.length) {
      setMessage("Please choose at least one file.");
      return;
    }
    await uploadImages(files);
    setFiles([]);
    await load();
    setMessage("Upload successful. Set alt text and publish below.");
  };

  const saveMeta = async (id: string, altText: string | null, published: boolean) => {
    if (published && !altText?.trim()) {
      setMessage("alt_text is required before publishing.");
      return;
    }
    const updated = await updateAdminUpload(id, {
      alt_text: altText?.trim() || null,
      published
    });
    setItems((prev) => prev.map((x) => (x.id === id ? updated : x)));
    setMessage("Upload metadata updated.");
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-stone-900 mb-4">Uploads Manager</h1>

      <form onSubmit={onSubmit} className="bg-white border border-stone-200 rounded-xl p-6 space-y-4 mb-6">
        <input
          type="file"
          multiple
          accept="image/jpeg,image/png,image/webp"
          onChange={(e) => setFiles(Array.from(e.target.files || []))}
        />
        <button className="bg-[#c83d26] text-white px-4 py-2 rounded">Upload</button>
        {message && <p className="text-sm text-stone-600">{message}</p>}
      </form>

      <div className="bg-white border border-stone-200 rounded-xl p-4 space-y-3">
        {items.map((item) => (
          <UploadRow key={item.id} item={item} onSave={saveMeta} />
        ))}
      </div>
    </div>
  );
}

function UploadRow({
  item,
  onSave
}: {
  item: UploadDTO;
  onSave: (id: string, altText: string | null, published: boolean) => Promise<void>;
}) {
  const [alt, setAlt] = useState(item.alt_text || "");
  const [published, setPublished] = useState(item.published);

  return (
    <div className="border border-stone-200 rounded p-3 space-y-2">
      <img src={item.url} alt={item.alt_text || item.key} className="h-32 object-cover rounded" />
      <input className="w-full border px-2 py-1 rounded" value={alt} onChange={(e) => setAlt(e.target.value)} placeholder="Alt text" />
      <label className="flex items-center gap-2 text-sm">
        <input type="checkbox" checked={published} onChange={(e) => setPublished(e.target.checked)} />
        Published
      </label>
      <button className="px-3 py-1 bg-stone-800 text-white rounded text-sm" onClick={() => onSave(item.id, alt, published)}>
        Save Metadata
      </button>
    </div>
  );
}
