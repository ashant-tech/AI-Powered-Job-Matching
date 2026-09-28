'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function RecommendationsPage() {
  const router = useRouter();
  const [matches, setMatches] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedCV, setSelectedCV] = useState<number | null>(null);
  const [cvs, setCvs] = useState<any[]>([]);
  const [cvAnalysis, setCvAnalysis] = useState<any>(null);
  const [expandedMatch, setExpandedMatch] = useState<number | null>(null);

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
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const toggleMatchExpansion = (matchId: number) => {
    setExpandedMatch(expandedMatch === matchId ? null : matchId);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-indigo-600">AI Job Matching</h1>
          <button
            onClick={() => router.push('/dashboard')}
            className="text-gray-600 hover:text-gray-900"
          >
            ← Back to Dashboard
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* CV Selection and Analysis */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-bold mb-4">Your CV Analysis</h2>
          {cvs.length === 0 ? (
            <div className="text-gray-600">
              No CVs uploaded. <button onClick={() => router.push('/upload-cv')} className="text-indigo-600 hover:underline">Upload a CV</button>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex gap-4 items-center">
                <select
                  value={selectedCV || ''}
                  onChange={(e) => setSelectedCV(Number(e.target.value))}
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                  {cvs.map((cv) => (
                    <option key={cv.id} value={cv.id}>
                      {cv.title} - {new Date(cv.created_at).toLocaleDateString()}
                    </option>
                  ))}
                </select>
                <button
                  onClick={handleFindMatches}
                  className="bg-indigo-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-indigo-700 transition"
                >
                  Find Matches
                </button>
              </div>

              {cvAnalysis && (
                <div className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-lg p-4 mt-4">
                  <h3 className="font-semibold text-lg mb-3">CV Insights</h3>
                  <div className="grid md:grid-cols-2 gap-4">
                    {cvAnalysis.experience_level && (
                      <div>
                        <span className="text-sm text-gray-600">Experience Level:</span>
                        <div className="font-semibold text-indigo-700">{cvAnalysis.experience_level}</div>
                      </div>
                    )}
                    {cvAnalysis.total_years_experience !== undefined && cvAnalysis.total_years_experience !== null && (
                      <div>
                        <span className="text-sm text-gray-600">Total Experience:</span>
                        <div className="font-semibold text-indigo-700">{cvAnalysis.total_years_experience}+ years</div>
                      </div>
                    )}
                    {cvAnalysis.skills && (
                      <div className="md:col-span-2">
                        <span className="text-sm text-gray-600">Key Skills:</span>
                        <div className="flex flex-wrap gap-2 mt-1">
                          {JSON.parse(cvAnalysis.skills).slice(0, 8).map((skill: string, index: number) => (
                            <span key={index} className="bg-indigo-100 text-indigo-800 px-2 py-1 rounded text-sm">
                              {skill}
                            </span>
                          ))}
                          {JSON.parse(cvAnalysis.skills).length > 8 && (
                            <span className="text-sm text-gray-500">+{JSON.parse(cvAnalysis.skills).length - 8} more</span>
                          )}
                        </div>
                      </div>
                    )}
                    {cvAnalysis.job_titles && (
                      <div className="md:col-span-2">
                        <span className="text-sm text-gray-600">Job Titles:</span>
                        <div className="font-semibold text-gray-800 mt-1">
                          {JSON.parse(cvAnalysis.job_titles).join(', ') || 'Not specified'}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Matches */}
        {loading ? (
          <div className="text-center py-8">
            <div className="text-xl">Finding matches...</div>
          </div>
        ) : error ? (
          <div role="alert" className="bg-red-50 text-red-700 rounded-lg p-6 text-center">
            {error}
          </div>
        ) : matches.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <div className="text-gray-600">
              {selectedCV ? 'No matches found. Try selecting a different CV or upload a new one.' : 'Select a CV to find matches'}
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Your Job Matches ({matches.length})</h2>
              <div className="text-sm text-gray-600">
                Sorted by match score
              </div>
            </div>
            {matches.map((match) => (
              <div key={match.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-xl font-bold text-gray-900">{match.job?.title || 'Job no longer available'}</h3>
                      <div className={`text-white px-3 py-1 rounded-full text-sm font-bold ${getMatchScoreColor(match.match_score)}`}>
                        {match.match_score}% Match
                      </div>
                    </div>
                    <div className="flex gap-4 text-sm text-gray-600 mb-3">
                      {match.job && <span className="font-medium">{match.job.company}</span>}
                      {match.job?.location && <span>📍 {match.job.location}</span>}
                      {match.job?.deadline && (
                        <span className="flex items-center gap-1">
                          ⏳ Apply by {new Date(match.job.deadline).toLocaleDateString()}
                        </span>
                      )}
                    </div>

                    {/* Detailed Match Reasons */}
                    {match.detailed_reasons && match.detailed_reasons.length > 0 && (
                      <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-3">
                        <div className="text-sm font-semibold text-green-800 mb-2">Why this job matches you:</div>
                        <ul className="text-sm text-green-700 space-y-1">
                          {match.detailed_reasons.slice(0, 3).map((reason: string, index: number) => (
                            <li key={index} className="flex items-start gap-2">
                              <span className="text-green-500">✓</span>
                              <span>{reason}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Expandable Details */}
                    {expandedMatch === match.id && (
                      <div className="mt-4 pt-4 border-t border-gray-200">
                        {/* Skill Gaps */}
                        {match.skill_gaps && match.skill_gaps.missing_skills && match.skill_gaps.missing_skills.length > 0 && (
                          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-3">
                            <div className="text-sm font-semibold text-yellow-800 mb-2">
                              Skill Gaps ({match.skill_gaps.gap_percentage}%):
                            </div>
                            <div className="text-sm text-yellow-700 mb-2">
                              Missing skills: {match.skill_gaps.missing_skills.join(', ')}
                            </div>
                            {match.skill_gaps.recommended_skills && match.skill_gaps.recommended_skills.length > 0 && (
                              <div className="text-sm text-yellow-700">
                                <div className="font-medium">Recommendations:</div>
                                <ul className="mt-1 space-y-1">
                                  {match.skill_gaps.recommended_skills.map((rec: string, index: number) => (
                                    <li key={index} className="flex items-start gap-2">
                                      <span>💡</span>
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
                            <div className="text-sm font-semibold text-gray-700 mb-1">Job Description:</div>
                            <div className="text-sm text-gray-600 line-clamp-3">
                              {match.job.description}
                            </div>
                          </div>
                        )}

                        {/* Requirements */}
                        {match.job?.requirements && (
                          <div>
                            <div className="text-sm font-semibold text-gray-700 mb-1">Requirements:</div>
                            <div className="text-sm text-gray-600">
                              {match.job.requirements}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  <div className="flex flex-col gap-2 ml-4">
                    <button
                      onClick={() => match.job?.apply_url && window.open(match.job.apply_url, '_blank', 'noopener,noreferrer')}
                      disabled={!match.job?.apply_url}
                      className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition disabled:opacity-50 text-sm font-semibold"
                    >
                      Apply
                    </button>
                    <button
                      onClick={() => toggleMatchExpansion(match.id)}
                      className="bg-indigo-100 text-indigo-700 px-4 py-2 rounded-lg hover:bg-indigo-200 transition text-sm font-semibold"
                    >
                      {expandedMatch === match.id ? 'Show Less' : 'Show Details'}
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
