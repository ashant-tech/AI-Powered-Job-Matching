"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import JobCard from "@/components/JobCard";
import MatchScore from "@/components/MatchScore";
import SkillBadge from "@/components/SkillBadge";
import { getLatestCV } from "@/services/cvApi";
import { getRecommendations, listNotifications } from "@/services/matchingApi";
import type { CV } from "@/types/CV";
import type { Match, Notification } from "@/types/Match";

export default function DashboardPage() {
  const [cv, setCv] = useState<CV | null>(null);
  const [matches, setMatches] = useState<Match[]>([]);
  const [unread, setUnread] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([getLatestCV(), getRecommendations(3), listNotifications(true)])
      .then(([c, m, n]) => {
        setCv(c);
        setMatches(m);
        setUnread(n);
      })
      .catch(() => undefined)
      .finally(() => setLoading(false));
  }, []);

  return (
    <AppShell title="Dashboard">
      {loading ? (
        <p className="text-slate-600">Loading…</p>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-3">
            <Stat label="Skills detected" value={cv ? cv.skills.length : 0} />
            <Stat label="Years of experience" value={cv ? cv.years_of_experience : 0} />
            <Stat label="Unread alerts" value={unread.length} href="/notifications" />
          </div>

          {!cv ? (
            <div className="card flex items-center justify-between">
              <div>
                <h2 className="font-semibold">Upload your CV to get started</h2>
                <p className="text-sm text-slate-600">We need your CV to find matching jobs.</p>
              </div>
              <Link href="/upload-cv" className="btn-primary">
                Upload CV
              </Link>
            </div>
          ) : (
            <div className="card space-y-2">
              <h2 className="font-semibold">Your profile</h2>
              <p className="text-sm text-slate-700">{cv.summary}</p>
              <div className="flex flex-wrap gap-1.5">
                {cv.skills.slice(0, 12).map((s) => (
                  <SkillBadge key={s.id} name={s.name} />
                ))}
              </div>
            </div>
          )}

          <section className="space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="font-semibold">Top matches</h2>
              <Link href="/recommendations" className="text-sm font-medium text-indigo-600 hover:underline">
                See all →
              </Link>
            </div>
            {matches.length === 0 ? (
              <p className="text-sm text-slate-600">No matches yet — run matching from the Recommendations page.</p>
            ) : (
              matches.map((m) => (
                <JobCard key={m.id} job={m.job}>
                  <MatchScore score={m.score} />
                </JobCard>
              ))
            )}
          </section>
        </>
      )}
    </AppShell>
  );
}

function Stat({ label, value, href }: { label: string; value: number; href?: string }) {
  const content = (
    <div className="card">
      <p className="text-sm text-slate-600">{label}</p>
      <p className="text-3xl font-bold text-slate-900">{value}</p>
    </div>
  );
  return href ? <Link href={href}>{content}</Link> : content;
}
