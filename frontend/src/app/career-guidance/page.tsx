'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function CareerGuidancePage() {
  const router = useRouter();
  const [careerPath, setCareerPath] = useState<any>(null);
  const [skillGaps, setSkillGaps] = useState<any>(null);
  const [roadmap, setRoadmap] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    fetchCareerGuidance();
  }, [router]);

  const fetchCareerGuidance = async () => {
    try {
      const token = localStorage.getItem('token');

      // Fetch career path
      const careerResponse = await fetch('/api/matching/career-guidance', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (careerResponse.ok) {
        const careerData = await careerResponse.json();
        setCareerPath(careerData);
      }

      // Fetch skill gaps
      const skillGapsResponse = await fetch('/api/matching/career-guidance/skill-gaps', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (skillGapsResponse.ok) {
        const skillGapsData = await skillGapsResponse.json();
        setSkillGaps(skillGapsData);
      }

      // Fetch roadmap
      const roadmapResponse = await fetch('/api/matching/career-guidance/roadmap', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (roadmapResponse.ok) {
        const roadmapData = await roadmapResponse.json();
        setRoadmap(roadmapData);
      }

    } catch (error) {
      console.error('Error fetching career guidance:', error);
      setError('Failed to load career guidance. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading career guidance...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-red-600">{error}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-indigo-600">Career Guidance</h1>
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
        {/* Current Career Status */}
        {careerPath && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Current Career Status</h2>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <div className="text-sm text-gray-600 mb-1">Current Level</div>
                <div className="text-2xl font-bold text-indigo-600 capitalize">
                  {careerPath.current_level.replace('_', ' ')}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600 mb-1">Field</div>
                <div className="text-2xl font-bold text-green-600 capitalize">
                  {careerPath.field.replace('_', ' ')}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600 mb-1">Current Title</div>
                <div className="text-lg font-semibold">
                  {careerPath.current_stage?.title}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600 mb-1">Career Progress</div>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-indigo-600 h-3 rounded-full transition-all"
                      style={{ width: `${careerPath.progress_percentage}%` }}
                    />
                  </div>
                  <span className="text-sm font-semibold">{careerPath.progress_percentage}%</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Skill Gaps Analysis */}
        {skillGaps && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Skill Gaps Analysis</h2>
            {skillGaps.message ? (
              <div className="bg-green-50 border border-green-200 p-4 rounded-lg">
                <div className="text-green-800">{skillGaps.message}</div>
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <div className="text-sm text-gray-600 mb-2">Current Skills</div>
                  <div className="flex flex-wrap gap-2">
                    {skillGaps.current_skills?.map((skill: string, index: number) => (
                      <span key={index} className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-600 mb-2">Required Skills for Next Level</div>
                  <div className="flex flex-wrap gap-2">
                    {skillGaps.required_skills?.map((skill: string, index: number) => (
                      <span
                        key={index}
                        className={`px-3 py-1 rounded-full text-sm ${
                          skillGaps.missing_skills?.includes(skill)
                            ? 'bg-red-100 text-red-800'
                            : 'bg-green-100 text-green-800'
                        }`}
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
                {skillGaps.missing_skills?.length > 0 && (
                  <div className="bg-red-50 border border-red-200 p-4 rounded-lg">
                    <div className="text-sm text-gray-600 mb-2">Missing Skills ({skillGaps.missing_skills.length})</div>
                    <div className="flex flex-wrap gap-2">
                      {skillGaps.missing_skills.map((skill: string, index: number) => (
                        <span key={index} className="bg-red-100 text-red-800 px-3 py-1 rounded-full text-sm">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {skillGaps.learning_resources?.length > 0 && (
                  <div>
                    <div className="text-sm text-gray-600 mb-2">Learning Resources</div>
                    <ul className="list-disc list-inside space-y-1">
                      {skillGaps.learning_resources.map((resource: string, index: number) => (
                        <li key={index} className="text-sm text-gray-700">{resource}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Career Roadmap */}
        {roadmap.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4">Career Roadmap</h2>
            <div className="space-y-4">
              {roadmap.map((stage, index) => (
                <div
                  key={index}
                  className={`p-4 rounded-lg border-2 ${
                    stage.is_current
                      ? 'border-indigo-500 bg-indigo-50'
                      : stage.is_next
                      ? 'border-green-500 bg-green-50'
                      : 'border-gray-200 bg-gray-50'
                  }`}
                >
                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0">
                      <div
                        className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-semibold ${
                          stage.is_current
                            ? 'bg-indigo-600'
                            : stage.is_next
                            ? 'bg-green-600'
                            : 'bg-gray-400'
                        }`}
                      >
                        {index + 1}
                      </div>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="text-lg font-semibold">{stage.title}</h3>
                        {stage.is_current && (
                          <span className="bg-indigo-100 text-indigo-800 px-2 py-1 rounded text-xs">
                            Current
                          </span>
                        )}
                        {stage.is_next && (
                          <span className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">
                            Next Goal
                          </span>
                        )}
                      </div>
                      <div className="mb-2">
                        <div className="text-sm text-gray-600 mb-1">Skills Required</div>
                        <div className="flex flex-wrap gap-1">
                          {stage.skills.map((skill: string, skillIndex: number) => (
                            <span key={skillIndex} className="bg-gray-200 text-gray-700 px-2 py-1 rounded text-xs">
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-600 mb-1">Requirements</div>
                        <ul className="list-disc list-inside text-sm text-gray-700">
                          {stage.requirements.map((req: string, reqIndex: number) => (
                            <li key={reqIndex}>{req}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
