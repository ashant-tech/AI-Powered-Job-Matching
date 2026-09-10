"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import Sidebar from "./Sidebar";
import { getToken } from "@/services/apiClient";

export default function AppShell({ title, children }: { title: string; children: React.ReactNode }) {
  const router = useRouter();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!getToken()) router.replace("/login");
    else setReady(true);
  }, [router]);

  if (!ready) return null;

  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-6 px-4 py-8 md:flex-row">
      <Sidebar />
      <main className="flex-1 space-y-6">
        <h1 className="text-2xl font-bold text-slate-900">{title}</h1>
        {children}
      </main>
    </div>
  );
}
