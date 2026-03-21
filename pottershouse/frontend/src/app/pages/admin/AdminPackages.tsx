import React, { useEffect, useState } from "react";
import { PackageDTO, createAdminPackage, fetchAdminPackages } from "../../lib/api";

export default function AdminPackages() {
  const [packages, setPackages] = useState<PackageDTO[]>([]);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("");
  const [active, setActive] = useState(true);

  useEffect(() => {
    fetchAdminPackages()
      .then((res) => setPackages(Array.isArray(res) ? (res as PackageDTO[]) : []))
      .catch(() => setPackages([]));
  }, []);

  const addPackage = async (e: React.FormEvent) => {
    e.preventDefault();
    const created = await createAdminPackage({
      name: name.trim(),
      description: description.trim(),
      price: Number(price),
      active
    });
    setPackages((prev) => [created, ...prev]);
    setName("");
    setDescription("");
    setPrice("");
    setActive(true);
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-stone-900 mb-4">Packages Manager</h1>

      <form onSubmit={addPackage} className="bg-white border border-stone-200 rounded-xl p-4 mb-6 space-y-3">
        <input className="border px-3 py-2 rounded w-full" placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} required />
        <textarea className="border px-3 py-2 rounded w-full" placeholder="Description" value={description} onChange={(e) => setDescription(e.target.value)} />
        <input className="border px-3 py-2 rounded w-full" placeholder="Price" type="number" min="0" step="0.01" value={price} onChange={(e) => setPrice(e.target.value)} required />
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={active} onChange={(e) => setActive(e.target.checked)} />
          Active
        </label>
        <button className="bg-[#c83d26] text-white rounded px-4 py-2">Add Package</button>
      </form>

      <div className="bg-white border border-stone-200 rounded-xl overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-stone-50 text-xs uppercase text-stone-500">
            <tr>
              <th className="px-6 py-3">Name</th>
              <th className="px-6 py-3">Price</th>
              <th className="px-6 py-3">Active</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-stone-200">
            {packages.map((p) => (
              <tr key={p.id}>
                <td className="px-6 py-3">{p.name}</td>
                <td className="px-6 py-3">P{p.price}</td>
                <td className="px-6 py-3">{p.active ? "Yes" : "No"}</td>
              </tr>
            ))}
            {packages.length === 0 && (
              <tr>
                <td colSpan={3} className="px-6 py-6 text-center text-sm text-stone-500">
                  No packages yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
