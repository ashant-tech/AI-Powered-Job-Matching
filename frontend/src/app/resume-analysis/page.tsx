'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function ResumeAnalysisPage() {
  const router = useRouter();
  const [analysis, setAnalysis] = useState<any>(null);
  const [tips, setTips] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    fetchResumeAnalysis();
  }, [router]);

  const fetchResumeAnalysis = async () => {
    try {
      const token = localStorage.getItem('token');

      // Fetch resume analysis
      const analysisResponse = await fetch('/api/matching/resume-analysis', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (analysisResponse.ok) {
        const analysisData = await analysisResponse.json();
        setAnalysis(analysisData);
      } else if (analysisResponse.status === 404) {
        setError('No CV found. Please upload your CV first to get resume analysis.');
        return;
      }

      // Fetch optimization tips
      const tipsResponse = await fetch('/api/matching/resume-analysis/tips', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (tipsResponse.ok) {
        const tipsData = await tipsResponse.json();
        setTips(tipsData);
      }

    } catch (error) {
      console.error('Error fetching resume analysis:', error);
      setError('Failed to load resume analysis. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Analyzing your resume...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-xl text-red-600 mb-4">{error}</div>
          <button
            onClick={() => router.push('/upload-cv')}
            className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700"
          >
            Upload CV
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-indigo-600">Resume Analysis</h1>
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
        {/* ATS Score */}
        {analysis && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">ATS-Friendliness Score</h2>
            <div className="flex items-center gap-6">
              <div className="flex-1">
                <div className="flex items-center gap-4 mb-4">
                  <div className="text-5xl font-bold text-indigo-600">{analysis.ats_score}%</div>
                  <div>
                    <div className="text-lg font-semibold capitalize">{analysis.ats_rating}</div>
                    <div className="text-sm text-gray-600">ATS Optimization</div>
                  </div>
                </div>
                <div className="bg-gray-200 rounded-full h-4">
                  <div
                    className={`h-4 rounded-full transition-all ${
                      analysis.ats_score >= 80 ? 'bg-green-600' :
                      analysis.ats_score >= 60 ? 'bg-yellow-500' :
                      analysis.ats_score >= 40 ? 'bg-orange-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${analysis.ats_score}%` }}
                  />
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-600 mb-1">Field</div>
                <div className="text-lg font-semibold capitalize">{analysis.field.replace('_', ' ')}</div>
                <div className="text-sm text-gray-600 mt-2 mb-1">Experience Level</div>
                <div className="text-lg font-semibold capitalize">{analysis.experience_level?.replace('_', ' ') || 'Unknown'}</div>
              </div>
            </div>
          </div>
        )}

        {/* Skill Analysis */}
        {analysis?.skill_analysis && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Skill Analysis</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <div className="text-sm text-gray-600 mb-2">Skills Found ({analysis.skill_analysis.found_skills.length})</div>
                <div className="flex flex-wrap gap-2">
                  {analysis.skill_analysis.found_skills.map((skill: string, index: number) => (
                    <span key={index} className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600 mb-2">Missing ATS Keywords ({analysis.skill_analysis.missing_ats_keywords.length})</div>
                <div className="flex flex-wrap gap-2">
                  {analysis.skill_analysis.missing_ats_keywords.map((skill: string, index: number) => (
                    <span key={index} className="bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm">
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            </div>
            <div className="mt-4">
              <div className="text-sm text-gray-600 mb-2">Skill Coverage</div>
              <div className="flex items-center gap-2">
                <div className="flex-1 bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-indigo-600 h-3 rounded-full transition-all"
                    style={{ width: `${analysis.skill_analysis.skill_coverage}%` }}
                  />
                </div>
                <span className="text-sm font-semibold">{analysis.skill_analysis.skill_coverage}%</span>
              </div>
            </div>
          </div>
        )}

        {/* Hidden Skills */}
        {analysis?.hidden_skills && analysis.hidden_skills.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Transferable & Hidden Skills</h2>
            <div className="text-sm text-gray-600 mb-3">
              These skills were identified from your experience descriptions:
            </div>
            <div className="flex flex-wrap gap-2">
              {analysis.hidden_skills.map((skill: string, index: number) => (
                <span key={index} className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm">
                  {skill}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Improvement Suggestions */}
        {analysis?.improvement_suggestions && analysis.improvement_suggestions.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Improvement Suggestions</h2>
            <div className="space-y-3">
              {analysis.improvement_suggestions.map((suggestion: string, index: number) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <div className="flex-shrink-0 w-6 h-6 bg-yellow-500 text-white rounded-full flex items-center justify-center text-sm font-semibold">
                    {index + 1}
                  </div>
                  <div className="text-sm text-gray-700">{suggestion}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Optimization Tips */}
        {tips.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Resume Optimization Tips</h2>
            <div className="space-y-3">
              {tips.map((tip: string, index: number) => (
                <div key={index} className="flex items-start gap-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex-shrink-0">💡</div>
                  <div className="text-sm text-gray-700">{tip}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
