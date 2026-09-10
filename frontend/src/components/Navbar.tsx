"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { getToken } from "@/services/apiClient";
import { logout } from "@/services/authApi";

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [authed, setAuthed] = useState(false);

  useEffect(() => {
    setAuthed(Boolean(getToken()));
  }, [pathname]);

  return (
    <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/90 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4">
        <Link href="/" className="text-lg font-bold text-indigo-700">
          JobMatch<span className="text-slate-900">AI</span>
        </Link>
        <nav className="flex items-center gap-3 text-sm">
          {authed ? (
            <>
              <Link href="/dashboard" className="text-slate-700 hover:text-indigo-700">
                Dashboard
              </Link>
              <button
                onClick={() => {
                  logout();
                  setAuthed(false);
                  router.push("/");
                }}
                className="btn-secondary"
              >
                Log out
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className="text-slate-700 hover:text-indigo-700">
                Log in
              </Link>
              <Link href="/register" className="btn-primary">
                Get started
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
