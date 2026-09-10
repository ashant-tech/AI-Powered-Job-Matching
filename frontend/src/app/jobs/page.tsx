"use client";

import { useEffect, useState } from "react";
import JobCard from "@/components/JobCard";
import { listJobs } from "@/services/jobApi";
import type { Job } from "@/types/Job";

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [q, setQ] = useState("");
  const [location, setLocation] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const handle = setTimeout(() => {
      setLoading(true);
      listJobs({ q, location })
        .then(setJobs)
        .catch(() => setJobs([]))
        .finally(() => setLoading(false));
    }, 300);
    return () => clearTimeout(handle);
  }, [q, location]);

  return (
    <main className="mx-auto max-w-4xl space-y-6 px-4 py-8">
      <h1 className="text-2xl font-bold">Browse jobs</h1>
      <div className="grid gap-3 sm:grid-cols-2">
        <input className="input" placeholder="Search title, company, keywords…" value={q} onChange={(e) => setQ(e.target.value)} />
        <input className="input" placeholder="Location" value={location} onChange={(e) => setLocation(e.target.value)} />
      </div>
      {loading ? (
        <p className="text-slate-600">Loading…</p>
      ) : jobs.length === 0 ? (
        <p className="text-slate-600">No jobs found.</p>
      ) : (
        <div className="space-y-4">
          {jobs.map((j) => (
            <JobCard key={j.id} job={j} />
          ))}
        </div>
      )}
    </main>
  );
}
