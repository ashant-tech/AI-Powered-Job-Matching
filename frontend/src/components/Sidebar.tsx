"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/dashboard", label: "Overview" },
  { href: "/upload-cv", label: "Upload CV" },
  { href: "/recommendations", label: "Recommendations" },
  { href: "/jobs", label: "Browse jobs" },
  { href: "/notifications", label: "Notifications" },
  { href: "/profile", label: "Profile" },
];

export default function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="w-full shrink-0 md:w-56">
      <nav className="flex gap-1 overflow-x-auto md:flex-col">
        {links.map((l) => {
          const active = pathname === l.href;
          return (
            <Link
              key={l.href}
              href={l.href}
              className={`whitespace-nowrap rounded-lg px-3 py-2 text-sm font-medium transition ${
                active ? "bg-indigo-600 text-white" : "text-slate-700 hover:bg-slate-200"
              }`}
            >
              {l.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
