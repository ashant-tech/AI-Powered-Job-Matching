"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { register } from "@/services/authApi";
import { ApiError } from "@/services/apiClient";

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({ full_name: "", email: "", password: "", phone: "" });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function update(field: keyof typeof form) {
    return (e: React.ChangeEvent<HTMLInputElement>) => setForm({ ...form, [field]: e.target.value });
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await register({ ...form, phone: form.phone || undefined });
      router.push("/upload-cv");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-md px-4 py-16">
      <div className="card space-y-5">
        <h1 className="text-2xl font-bold">Create your account</h1>
        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-sm font-medium">Full name</label>
            <input className="input" required value={form.full_name} onChange={update("full_name")} />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Email</label>
            <input className="input" type="email" required value={form.email} onChange={update("email")} />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Phone (optional, for SMS alerts)</label>
            <input className="input" value={form.phone} onChange={update("phone")} />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Password</label>
            <input className="input" type="password" minLength={8} required value={form.password} onChange={update("password")} />
          </div>
          {error && <p className="text-sm text-rose-600">{error}</p>}
          <button className="btn-primary w-full" disabled={loading}>
            {loading ? "Creating…" : "Register"}
          </button>
        </form>
        <p className="text-center text-sm text-slate-600">
          Already registered?{" "}
          <Link href="/login" className="font-medium text-indigo-600 hover:underline">
            Log in
          </Link>
        </p>
      </div>
    </main>
  );
}
