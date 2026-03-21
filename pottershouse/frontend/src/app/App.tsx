import React, { Suspense } from "react";
import { RouterProvider } from "react-router";
import { router } from "./routes";
import { Toaster } from "sonner";

export default function App() {
  return (
    <>
      <Suspense fallback={<div className="p-6 text-stone-600">Loading...</div>}>
        <RouterProvider router={router} />
      </Suspense>
      <Toaster position="top-center" richColors />
    </>
  );
}
