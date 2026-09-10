"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import ProfileCard from "@/components/ProfileCard";
import { getMe, updateMe } from "@/services/authApi";
import { getLatestCV } from "@/services/cvApi";
import type { CV } from "@/types/CV";
import type { User } from "@/types/User";

export default function ProfilePage() {
  const [user, setUser] = useState<User | null>(null);
  const [cv, setCv] = useState<CV | null>(null);
  const [form, setForm] = useState({ full_name: "", phone: "" });
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    Promise.all([getMe(), getLatestCV()])
      .then(([u, c]) => {
        setUser(u);
        setCv(c);
        setForm({ full_name: u.full_name, phone: u.phone ?? "" });
      })
      .catch(() => undefined);
  }, []);

  async function save(e: React.FormEvent) {
    e.preventDefault();
    const updated = await updateMe(form);
    setUser(updated);
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  }

  return (
    <AppShell title="Profile">
      {user && (
        <div className="grid gap-6 lg:grid-cols-2">
          <ProfileCard user={user} cv={cv} />
          <form onSubmit={save} className="card space-y-4">
            <h2 className="font-semibold">Edit details</h2>
            <div>
              <label className="mb-1 block text-sm font-medium">Full name</label>
              <input className="input" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Phone</label>
              <input className="input" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
            </div>
            <button className="btn-primary">{saved ? "Saved" : "Save changes"}</button>
          </form>
        </div>
      )}
    </AppShell>
  );
}
