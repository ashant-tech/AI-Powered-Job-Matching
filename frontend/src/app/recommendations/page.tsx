'use client';

import { useEffect, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { matchingApi } from '../../services/matchingApi';
import { Match } from '../../types/Match';

function parseList(value?: string): string[] {
  if (!value) return [];
  try {
    const parsed = JSON.parse(value);
    return Array.isArray(parsed) ? parsed.filter((item): item is string => typeof item === 'string') : [];
  } catch {
    return value.split(/[,;\n]/).map((item) => item.trim()).filter(Boolean);
  }
}

export default function RecommendationsPage() {
  const router = useRouter();
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedCV, setSelectedCV] = useState<number | null>(null);
  const [cvs, setCvs] = useState<any[]>([]);
  const [cvAnalysis, setCvAnalysis] = useState<any>(null);
  const [expandedMatch, setExpandedMatch] = useState<number | null>(null);
  const markedViewed = useRef<Set<number>>(new Set());

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    fetchCVs();
  }, [router]);

  const fetchCVs = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const userData = await response.json();
        const cvsResponse = await fetch(`/api/cv/user/${userData.id}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (cvsResponse.ok) {
          const cvsData = await cvsResponse.json();
          setCvs(cvsData);
          if (cvsData.length > 0) {
            setSelectedCV(cvsData[0].id);
            setCvAnalysis(cvsData[0]);
            fetchMatches(cvsData[0].id);
          } else {
            setLoading(false);
          }
        }
      }
    } catch (error) {
      console.error('Error fetching CVs:', error);
      setLoading(false);
    }
  };

  const fetchMatches = async (cvId: number) => {
    setError('');
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/matching/cv/${cvId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const matchesData = await response.json();
        setMatches(matchesData);
      } else {
        const responseBody = await response.text();
        let errorMessage = `Finding matches failed (HTTP ${response.status})`;
        try {
          const errorData = JSON.parse(responseBody);
          if (typeof errorData.detail === 'string') {
            errorMessage = errorData.detail;
          }
        } catch {}
        setMatches([]);
        setError(errorMessage);
      }
    } catch (error) {
      console.error('Error fetching matches:', error);
      setMatches([]);
      setError(error instanceof Error ? error.message : 'Could not reach the matching service');
    } finally {
      setLoading(false);
    }
  };

  const handleFindMatches = () => {
    if (selectedCV) {
      setLoading(true);
      const selectedCVData = cvs.find(cv => cv.id === selectedCV);
      setCvAnalysis(selectedCVData);
      fetchMatches(selectedCV);
    }
  };

  const getMatchScoreColor = (score: number) => {
    if (score >= 80) return 'bg-emerald-500';
    if (score >= 60) return 'bg-amber-500';
    return 'bg-slate-400';
  };

  const markMatchViewed = async (match: any) => {
    if (!match?.id || match.status === 'viewed' || markedViewed.current.has(match.id)) {
      return;
    }
    markedViewed.current.add(match.id);
    const token = localStorage.getItem('token');
    if (!token) return;
    try {
      await matchingApi.updateMatchStatus(token, match.id, 'viewed');
      setMatches((prev) =>
        prev.map((m) => (m.id === match.id ? { ...m, status: 'viewed' } : m))
      );
    } catch (error) {
      // View-tracking is best-effort; let a later expansion retry.
      markedViewed.current.delete(match.id);
      console.error('Failed to mark match viewed:', error);
    }
  };

  const toggleMatchExpansion = (matchId: number) => {
    const opening = expandedMatch !== matchId;
    setExpandedMatch(opening ? matchId : null);
    if (opening) {
      markMatchViewed(matches.find((m) => m.id === matchId));
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      {/* Header */}
      <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/95 shadow-sm backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
          <button onClick={() => router.push('/')} className="flex items-center gap-3 text-slate-900">
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 text-white shadow-sm">
              <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">
                <rect x="3" y="7" width="18" height="13" rx="2.5" />
                <path d="M8 7V5.5A1.5 1.5 0 0 1 9.5 4h5A1.5 1.5 0 0 1 16 5.5V7M3 12h18m-11 0v2h4v-2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </span>
            <span className="text-base font-bold tracking-tight sm:text-lg">AI Job Matching</span>
          </button>
          <button
            onClick={() => router.push('/dashboard')}
            className="rounded-lg px-3 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 hover:text-slate-900"
          >
            <span aria-hidden="true">← </span>Dashboard
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-7 sm:px-6 sm:py-10 lg:px-8">
        <div className="mb-7">
          <p className="text-sm font-semibold text-indigo-600">Personalized for you</p>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight text-slate-950 sm:text-4xl">Your job matches</h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600 sm:text-base">
            Choose a CV to discover opportunities that fit your experience and skills.
          </p>
        </div>

        {/* CV Selection and Analysis */}
        <section className="mb-7 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
          <div className="mb-5 flex items-start gap-4">
            <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
              <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" stroke="currentColor" strokeWidth="1.7" aria-hidden="true">
                <path d="M7 3.5h7l4 4V20a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V4.5a1 1 0 0 1 1-1Z" strokeLinejoin="round" />
                <path d="M14 4v4h4M9 13h6M9 16h6" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </span>
            <div>
              <h2 className="text-lg font-semibold text-slate-900">Choose your CV</h2>
              <p className="mt-1 text-sm text-slate-500">We’ll use its experience and skills to find relevant roles.</p>
            </div>
          </div>
          {cvs.length === 0 ? (
            <div className="rounded-xl border border-dashed border-slate-300 bg-slate-50 px-5 py-8 text-center">
              <p className="font-semibold text-slate-800">Upload a CV to get started</p>
              <p className="mt-1 text-sm text-slate-500">Your CV helps us look for roles related to your experience.</p>
              <button onClick={() => router.push('/upload-cv')} className="mt-4 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-indigo-700">
                Upload a CV
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
                <select
                  value={selectedCV || ''}
                  onChange={(e) => setSelectedCV(Number(e.target.value))}
                  aria-label="Select a CV"
                  className="min-w-0 flex-1 rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-800 outline-none transition hover:border-slate-400 focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10"
                >
                  {cvs.map((cv) => (
                    <option key={cv.id} value={cv.id}>
                      {cv.title} - {new Date(cv.created_at).toLocaleDateString()}
                    </option>
                  ))}
                </select>
                <button
                  onClick={handleFindMatches}
                  disabled={!selectedCV || loading}
                  className="rounded-xl bg-indigo-600 px-6 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-indigo-700 focus:outline-none focus:ring-4 focus:ring-indigo-500/20 disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {loading ? 'Finding matches...' : 'Find matches'}
                </button>
              </div>

              {cvAnalysis && (
                <div className="mt-5 rounded-2xl border border-indigo-100 bg-gradient-to-br from-indigo-50/80 to-white p-4 sm:p-5">
                  <div className="mb-4 flex items-center justify-between gap-3">
                    <div>
                      <h3 className="font-semibold text-slate-900">Profile insights</h3>
                      <p className="mt-1 text-xs text-slate-500">Details detected from your selected CV.</p>
                    </div>
                    <span className="rounded-full bg-white px-3 py-1 text-xs font-medium text-indigo-700 ring-1 ring-indigo-100">CV analysis</span>
                  </div>
                  <div className="grid gap-4 sm:grid-cols-2">
                    {cvAnalysis.experience_level && (
                      <div className="rounded-xl border border-white bg-white/80 p-3">
                        <span className="text-xs font-medium uppercase tracking-wide text-slate-500">Experience level</span>
                        <div className="mt-1 font-semibold text-slate-900">{cvAnalysis.experience_level}</div>
                      </div>
                    )}
                    {cvAnalysis.total_years_experience !== undefined && cvAnalysis.total_years_experience !== null && (
                      <div className="rounded-xl border border-white bg-white/80 p-3">
                        <span className="text-xs font-medium uppercase tracking-wide text-slate-500">Total experience</span>
                        <div className="mt-1 font-semibold text-slate-900">{cvAnalysis.total_years_experience}+ years</div>
                      </div>
                    )}
                    {cvAnalysis.skills && (
                      <div className="sm:col-span-2">
                        <span className="text-xs font-medium uppercase tracking-wide text-slate-500">Key skills</span>
                        <div className="mt-2 flex flex-wrap gap-2">
                          {parseList(cvAnalysis.skills).slice(0, 8).map((skill: string, index: number) => (
                            <span key={index} className="rounded-lg border border-indigo-100 bg-white px-2.5 py-1.5 text-xs font-medium text-indigo-800">
                              {skill}
                            </span>
                          ))}
                          {parseList(cvAnalysis.skills).length > 8 && (
                            <span className="self-center text-xs text-slate-500">+{parseList(cvAnalysis.skills).length - 8} more</span>
                          )}
                        </div>
                      </div>
                    )}
                    {cvAnalysis.job_titles && (
                      <div className="sm:col-span-2">
                        <span className="text-xs font-medium uppercase tracking-wide text-slate-500">Related job titles</span>
                        <div className="mt-1 font-medium text-slate-800">
                          {JSON.parse(cvAnalysis.job_titles).join(', ') || 'Not specified'}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </section>

        {/* Matches */}
        {loading ? (
          <div role="status" className="rounded-2xl border border-slate-200 bg-white px-6 py-16 text-center shadow-sm">
            <span className="mx-auto flex h-11 w-11 items-center justify-center rounded-full bg-indigo-50">
              <span className="h-5 w-5 animate-spin rounded-full border-2 border-indigo-200 border-t-indigo-600" />
            </span>
            <p className="mt-4 font-semibold text-slate-900">Finding relevant roles</p>
            <p className="mt-1 text-sm text-slate-500">Comparing your CV with available jobs.</p>
          </div>
        ) : error ? (
          <div role="alert" className="rounded-2xl border border-red-200 bg-red-50 p-5 text-sm leading-6 text-red-800">
            <p className="font-semibold">We couldn’t find matches</p>
            <p className="mt-1">{error}</p>
            {selectedCV && (
              <button onClick={handleFindMatches} className="mt-3 rounded-lg bg-white px-3 py-2 font-semibold text-red-800 shadow-sm ring-1 ring-red-200 transition hover:bg-red-100">
                Try again
              </button>
            )}
          </div>
        ) : matches.length === 0 ? (
          <div className="rounded-2xl border border-slate-200 bg-white px-6 py-12 text-center shadow-sm">
            <span className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100 text-slate-500">
              <svg viewBox="0 0 24 24" fill="none" className="h-7 w-7" stroke="currentColor" strokeWidth="1.7" aria-hidden="true">
                <circle cx="10.8" cy="10.8" r="6.8" />
                <path d="m16 16 4 4M8 10.8h5.6" strokeLinecap="round" />
              </svg>
            </span>
            <h2 className="mt-4 text-lg font-semibold text-slate-900">{selectedCV ? 'No matches found yet' : 'Select a CV to find matches'}</h2>
            <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500">
              {selectedCV ? 'Try another CV or update your experience and skills to discover more relevant opportunities.' : 'Choose one of your uploaded CVs above to see matching roles.'}
            </p>
            {selectedCV && (
              <button onClick={() => router.push('/upload-cv')} className="mt-5 rounded-xl border border-slate-300 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50">
                Update your CV
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            <div className="mb-4 flex flex-wrap items-end justify-between gap-2">
              <div>
                <h2 className="text-xl font-semibold text-slate-950">Best matches</h2>
                <p className="mt-1 text-sm text-slate-500">{matches.length} opportunities, ranked by CV fit signals—not a prediction of hiring outcomes.</p>
              </div>
            </div>
            {matches.map((match) => (
              <article key={match.id} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:border-indigo-200 hover:shadow-lg hover:shadow-slate-200/60 sm:p-6">
                <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2.5">
                      <h3 className="text-lg font-semibold tracking-tight text-slate-950 sm:text-xl">{match.job?.title || 'Job no longer available'}</h3>
                      <span className="inline-flex items-center gap-2 rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700">
                        <span className={`h-2 w-2 rounded-full ${getMatchScoreColor(match.match_score)}`} />
                        {match.fit_level || 'Possible'} fit · {Math.round(match.match_score)}%
                      </span>
                    </div>
                    <div className="mt-2 flex flex-wrap gap-x-4 gap-y-2 text-sm text-slate-600">
                      {match.job && <span className="font-medium text-slate-800">{match.job.company}</span>}
                      {match.job?.location && (
                        <span className="inline-flex items-center gap-1.5">
                          <svg viewBox="0 0 20 20" fill="none" className="h-4 w-4 text-slate-400" stroke="currentColor" strokeWidth="1.6" aria-hidden="true">
                            <path d="M16 8.3c0 4.2-6 9-6 9s-6-4.8-6-9a6 6 0 1 1 12 0Z" />
                            <circle cx="10" cy="8" r="2" />
                          </svg>
                          {match.job.location}
                        </span>
                      )}
                      {match.job?.deadline && (
                        <span className="inline-flex items-center gap-1.5">
                          <svg viewBox="0 0 20 20" fill="none" className="h-4 w-4 text-slate-400" stroke="currentColor" strokeWidth="1.6" aria-hidden="true">
                            <circle cx="10" cy="10" r="7.5" />
                            <path d="M10 5.5v4.8l3 1.8" strokeLinecap="round" strokeLinejoin="round" />
                          </svg>
                          Apply by {new Date(match.job.deadline).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                    <div
                      role="meter"
                      aria-label={`Match score ${match.match_score}%`}
                      aria-valuemin={0}
                      aria-valuemax={100}
                      aria-valuenow={Math.min(100, Math.max(0, Number(match.match_score) || 0))}
                      className="mt-4 h-1.5 overflow-hidden rounded-full bg-slate-100"
                    >
                      <div
                        className={`h-full rounded-full ${getMatchScoreColor(match.match_score)}`}
                        style={{ width: `${Math.min(100, Math.max(0, Number(match.match_score) || 0))}%` }}
                      />
                    </div>
                    {match.score_confidence !== undefined && (
                      <p className="mt-2 text-xs text-slate-500">
                        Estimate uses {Math.round(match.score_confidence)}% of the CV and job signals available.
                      </p>
                    )}

                    {/* Detailed Match Reasons */}
                    {match.detailed_reasons && match.detailed_reasons.length > 0 && (
                      <div className="mt-4 rounded-xl border border-emerald-100 bg-emerald-50/70 p-4">
                        <div className="mb-2 text-sm font-semibold text-emerald-900">Why it may fit</div>
                        <ul className="space-y-2 text-sm text-emerald-900/80">
                          {match.detailed_reasons.slice(0, 3).map((reason: string, index: number) => (
                            <li key={index} className="flex items-start gap-2">
                              <svg viewBox="0 0 20 20" fill="none" className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" stroke="currentColor" strokeWidth="2" aria-hidden="true">
                                <path d="m4 10 4 4 8-8" strokeLinecap="round" strokeLinejoin="round" />
                              </svg>
                              <span className="leading-5">{reason}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {match.match_caveats?.map((caveat, index) => (
                      <p key={index} className="mt-3 rounded-lg bg-amber-50 px-3 py-2 text-xs leading-5 text-amber-900">
                        {caveat}
                      </p>
                    ))}

                    {/* Expandable Details */}
                    {expandedMatch === match.id && (
                      <div className="mt-5 space-y-4 border-t border-slate-100 pt-5">
                        {/* Skill Gaps */}
                        {match.skill_gaps && match.skill_gaps.missing_skills && match.skill_gaps.missing_skills.length > 0 && (
                          <div className="rounded-xl border border-amber-200 bg-amber-50 p-4">
                            <div className="mb-2 text-sm font-semibold text-amber-900">
                              Skills mentioned in the job but not found in your CV
                            </div>
                            <div className="mb-2 text-sm leading-6 text-amber-900/80">
                              These are signals to review, not confirmed requirements: {match.skill_gaps.missing_skills.join(', ')}
                            </div>
                            {match.skill_gaps.recommended_skills && match.skill_gaps.recommended_skills.length > 0 && (
                              <div className="text-sm text-amber-900/80">
                                <div className="font-medium">Recommendations:</div>
                                <ul className="mt-1 space-y-1">
                                  {match.skill_gaps.recommended_skills.map((rec: string, index: number) => (
                                    <li key={index} className="flex items-start gap-2">
                                      <span className="text-amber-700">•</span>
                                      <span>{rec}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                        )}

                        {/* Job Description */}
                        {match.job?.description && (
                          <div className="mb-3">
                            <div className="mb-1 text-sm font-semibold text-slate-800">Job description</div>
                            <div className="line-clamp-3 text-sm leading-6 text-slate-600">
                              {match.job.description}
                            </div>
                          </div>
                        )}

                        {/* Requirements */}
                        {match.job?.requirements && (
                          <div>
                            <div className="mb-1 text-sm font-semibold text-slate-800">Requirements</div>
                            <div className="text-sm leading-6 text-slate-600">
                              {match.job.requirements}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  <div className="flex flex-col gap-2 sm:ml-4 sm:min-w-36">
                    <button
                      onClick={() => match.job?.apply_url && window.open(match.job.apply_url, '_blank', 'noopener,noreferrer')}
                      disabled={!match.job?.apply_url}
                      className="rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-indigo-700 focus:outline-none focus:ring-4 focus:ring-indigo-500/20 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      Apply
                    </button>
                    <button
                      onClick={() => toggleMatchExpansion(match.id)}
                      aria-expanded={expandedMatch === match.id}
                      className="rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 focus:outline-none focus:ring-4 focus:ring-indigo-500/10"
                    >
                      {expandedMatch === match.id ? 'Show Less' : 'Show Details'}
                    </button>
                  </div>
                </div>
                  </article>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
