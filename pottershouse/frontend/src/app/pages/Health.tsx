import React, { useEffect, useState } from "react";
import { fetchHealth } from "../lib/api";

export default function Health() {
  const [status, setStatus] = useState<"checking" | "online" | "offline">("checking");

  useEffect(() => {
    let mounted = true;
    fetchHealth()
      .then(() => mounted && setStatus("online"))
      .catch(() => mounted && setStatus("offline"));
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className="min-h-screen bg-stone-50 py-16">
      <div className="max-w-xl mx-auto px-4 text-center">
        <h1 className="text-3xl font-bold text-stone-900">Health Check</h1>
        <p className="mt-2 text-stone-600">
          API status:{" "}
          <span className={status === "online" ? "text-green-600" : status === "offline" ? "text-red-600" : "text-stone-600"}>
            {status === "checking" ? "Checking..." : status}
          </span>
        </p>
      </div>
    </div>
  );
}
