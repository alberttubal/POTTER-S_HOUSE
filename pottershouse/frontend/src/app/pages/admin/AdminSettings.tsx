import React, { useEffect, useState } from "react";
import {
  SettingDTO,
  createAdminSetting,
  fetchAdminSettings,
  updateAdminSetting
} from "../../lib/api";

const PHONE_KEY = "contact_phone";
const ADDRESS_KEY = "business_address";

function toStringValue(value: unknown) {
  return typeof value === "string" ? value : "";
}

export default function AdminSettings() {
  const [rows, setRows] = useState<SettingDTO[]>([]);
  const [phone, setPhone] = useState("");
  const [address, setAddress] = useState("");
  const [message, setMessage] = useState("");

  const load = async () => {
    const data = await fetchAdminSettings();
    const list = Array.isArray(data) ? data : [];
    setRows(list);

    const phoneRow = list.find((x) => x.key === PHONE_KEY);
    const addressRow = list.find((x) => x.key === ADDRESS_KEY);

    setPhone(phoneRow ? toStringValue(phoneRow.value) : "");
    setAddress(addressRow ? toStringValue(addressRow.value) : "");
  };

  useEffect(() => {
    load().catch(() => {});
  }, []);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage("");

    const phoneRow = rows.find((x) => x.key === PHONE_KEY);
    const addressRow = rows.find((x) => x.key === ADDRESS_KEY);

    if (phoneRow) {
      await updateAdminSetting(phoneRow.id, { value: phone.trim() });
    } else {
      await createAdminSetting({ key: PHONE_KEY, value: phone.trim() });
    }

    if (addressRow) {
      await updateAdminSetting(addressRow.id, { value: address.trim() });
    } else {
      await createAdminSetting({ key: ADDRESS_KEY, value: address.trim() });
    }

    await load();
    setMessage("Saved.");
  };

  return (
    <div>
      <h1 className="text-2xl font-bold text-stone-900 mb-4">Settings</h1>
      <form onSubmit={onSubmit} className="bg-white border border-stone-200 rounded-xl p-6 space-y-4">
        <input className="w-full border px-3 py-2 rounded" placeholder="Owner Phone" value={phone} onChange={(e) => setPhone(e.target.value)} />
        <input className="w-full border px-3 py-2 rounded" placeholder="Business Address" value={address} onChange={(e) => setAddress(e.target.value)} />
        <button className="bg-[#c83d26] text-white px-4 py-2 rounded">Save</button>
        {message && <p className="text-sm text-stone-600">{message}</p>}
      </form>
    </div>
  );
}
