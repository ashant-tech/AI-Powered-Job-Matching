"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import JobCard from "@/components/JobCard";
import MatchScore from "@/components/MatchScore";
import SkillBadge from "@/components/SkillBadge";
import { ApiError } from "@/services/apiClient";
import { getRecommendations, runMatching } from "@/services/matchingApi";
import type { Match } from "@/types/Match";

export default function RecommendationsPage() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getRecommendations()
      .then(setMatches)
      .catch(() => undefined)
      .finally(() => setLoading(false));
  }, []);

  async function refresh() {
    setRunning(true);
    setError(null);
    try {
      setMatches(await runMatching());
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Matching failed");
    } finally {
      setRunning(false);
    }
  }

  return (
    <AppShell title="Recommended for you">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-600">Jobs ranked by how well they fit your latest CV.</p>
        <button className="btn-primary" onClick={refresh} disabled={running}>
          {running ? "Matching…" : "Run matching"}
        </button>
      </div>
      {error && <p className="text-sm text-rose-600">{error}</p>}
      {loading ? (
        <p className="text-slate-600">Loading…</p>
      ) : matches.length === 0 ? (
        <p className="text-slate-600">No recommendations yet. Upload a CV, then click “Run matching”.</p>
      ) : (
        <div className="space-y-4">
          {matches.map((m) => (
            <JobCard key={m.id} job={m.job}>
              <div className="flex flex-col items-end gap-2">
                <MatchScore score={m.score} size="lg" />
                <div className="text-right text-xs text-slate-500">
                  skills {Math.round(m.skill_score)}% · semantic {Math.round(m.semantic_score)}% · exp{" "}
                  {Math.round(m.experience_score)}%
                </div>
                <div className="flex max-w-xs flex-wrap justify-end gap-1">
                  {m.matched_skills.map((s) => (
                    <SkillBadge key={s} name={s} variant="matched" />
                  ))}
                  {m.missing_skills.map((s) => (
                    <SkillBadge key={s} name={s} variant="missing" />
                  ))}
                </div>
              </div>
            </JobCard>
          ))}
        </div>
      )}
    </AppShell>
  );
}
