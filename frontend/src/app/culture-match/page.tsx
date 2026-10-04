'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function CultureMatchPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<any[]>([]);
  const [selectedJob, setSelectedJob] = useState<any>(null);
  const [cultureAnalysis, setCultureAnalysis] = useState<any>(null);
  const [workStyle, setWorkStyle] = useState('collaborative');
  const [cultureMatch, setCultureMatch] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    fetchJobs();
  }, [router]);

  const fetchJobs = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/jobs/', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const jobsData = await response.json();
        setJobs(jobsData.slice(0, 10));
      }
    } catch (error) {
      console.error('Error fetching jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  const analyzeCulture = async (job: any) => {
    setSelectedJob(job);
    setLoading(true);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/matching/company-culture/${job.external_id}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const analysisData = await response.json();
        setCultureAnalysis(analysisData);
      }
    } catch (error) {
      console.error('Error analyzing culture:', error);
    } finally {
      setLoading(false);
    }
  };

  const matchCulture = async () => {
    if (!selectedJob) return;
    setLoading(true);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/matching/company-culture/match/${selectedJob.external_id}?work_style=${workStyle}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const matchData = await response.json();
        setCultureMatch(matchData);
      }
    } catch (error) {
      console.error('Error matching culture:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading culture analysis...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-indigo-600">Company Culture Match</h1>
          <button
            onClick={() => router.push('/dashboard')}
            className="text-gray-600 hover:text-gray-900"
          >
            ← Back to Dashboard
          </button>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {!selectedJob ? (
          <div>
            <h2 className="text-xl font-semibold mb-4">Select a Job to Analyze Culture</h2>
            <div className="grid md:grid-cols-2 gap-4">
              {jobs.map((job) => (
                <div
                  key={job.external_id}
                  onClick={() => analyzeCulture(job)}
                  className="bg-white p-4 rounded-lg shadow-md hover:shadow-lg transition cursor-pointer"
                >
                  <h3 className="font-semibold">{job.title}</h3>
                  <p className="text-gray-600">{job.company}</p>
                  <p className="text-sm text-gray-500">{job.location}</p>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div>
            <div className="mb-4">
              <button
                onClick={() => setSelectedJob(null)}
                className="text-indigo-600 hover:text-indigo-900"
              >
                ← Back to Job Selection
              </button>
            </div>
            
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <h2 className="text-xl font-semibold mb-2">{selectedJob.title} at {selectedJob.company}</h2>
              <p className="text-gray-600 mb-4">Company Culture Analysis</p>
              
              {cultureAnalysis && (
                <div className="space-y-4">
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <div className="text-sm text-gray-600 mb-1">Primary Culture</div>
                      <div className="text-lg font-semibold capitalize">{cultureAnalysis.primary_culture.replace('_', ' ')}</div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600 mb-1">Culture Profile</div>
                      <div className="text-gray-700">{cultureAnalysis.culture_profile}</div>
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold mb-2">Detected Cultures</h3>
                    <div className="flex flex-wrap gap-2">
                      {cultureAnalysis.detected_cultures.map((culture: any, index: number) => (
                        <span key={index} className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm">
                          {culture.type.replace('_', ' ')} ({culture.score})
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div>
                    <h3 className="font-semibold mb-2">Work Environment</h3>
                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <div className="text-sm text-gray-600">Pace</div>
                        <div className="capitalize">{cultureAnalysis.work_environment.pace}</div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-600">Structure</div>
                        <div className="capitalize">{cultureAnalysis.work_environment.structure}</div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-600">Collaboration</div>
                        <div className="capitalize">{cultureAnalysis.work_environment.collaboration}</div>
                      </div>
                      <div>
                        <div className="text-sm text-gray-600">Flexibility</div>
                        <div className="capitalize">{cultureAnalysis.work_environment.flexibility}</div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
            
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="font-semibold mb-4">Match Your Work Style</h3>
              <div className="mb-4">
                <label className="block text-sm text-gray-600 mb-2">Your Work Style</label>
                <select
                  value={workStyle}
                  onChange={(e) => setWorkStyle(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="collaborative">Collaborative</option>
                  <option value="independent">Independent</option>
                  <option value="structured">Structured</option>
                  <option value="flexible">Flexible</option>
                  <option value="fast_paced">Fast-paced</option>
                  <option value="steady">Steady</option>
                  <option value="leadership">Leadership</option>
                  <option value="specialist">Specialist</option>
                </select>
              </div>
              
              <button
                onClick={matchCulture}
                className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
              >
                Analyze Culture Fit
              </button>
              
              {cultureMatch && (
                <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <h4 className="font-semibold mb-2">Culture Fit Analysis</h4>
                  <div className="text-2xl font-bold text-blue-600 mb-2">{cultureMatch.fit_score}%</div>
                  <div className="text-lg font-semibold capitalize mb-2">{cultureMatch.fit_rating}</div>
                  <p className="text-gray-700 mb-4">{cultureMatch.fit_analysis}</p>
                  
                  <div>
                    <h5 className="font-semibold mb-2">Recommendations</h5>
                    <ul className="list-disc list-inside space-y-1">
                      {cultureMatch.recommendations.map((rec: string, index: number) => (
                        <li key={index} className="text-gray-700">{rec}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
