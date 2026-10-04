'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function SalaryNegotiationPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<any[]>([]);
  const [selectedJob, setSelectedJob] = useState<any>(null);
  const [offerAnalysis, setOfferAnalysis] = useState<any>(null);
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

  const analyzeOffer = async (job: any) => {
    setSelectedJob(job);
    setLoading(true);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/matching/salary-analysis/${job.external_id}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const analysisData = await response.json();
        setOfferAnalysis(analysisData);
      }
    } catch (error) {
      console.error('Error analyzing offer:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading salary analysis...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-indigo-600">Salary Negotiation</h1>
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
            <h2 className="text-xl font-semibold mb-4">Select a Job to Analyze Salary</h2>
            <div className="grid md:grid-cols-2 gap-4">
              {jobs.map((job) => (
                <div
                  key={job.external_id}
                  onClick={() => analyzeOffer(job)}
                  className="bg-white p-4 rounded-lg shadow-md hover:shadow-lg transition cursor-pointer"
                >
                  <h3 className="font-semibold">{job.title}</h3>
                  <p className="text-gray-600">{job.company}</p>
                  <p className="text-sm text-gray-500">{job.salary_min ? `$${job.salary_min.toLocaleString()}` : 'Salary not specified'}</p>
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
              <p className="text-gray-600 mb-4">Salary Analysis</p>
              
              {offerAnalysis && (
                <div className="space-y-4">
                  <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <h3 className="font-semibold mb-2">Offer Competitiveness</h3>
                    <div className="text-2xl font-bold text-blue-600">{offerAnalysis.competitiveness_score}%</div>
                    <div className="text-sm text-gray-600 capitalize">{offerAnalysis.competitiveness}</div>
                  </div>
                  
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <h3 className="font-semibold mb-2">Job Salary</h3>
                      <div className="text-gray-700">
                        Min: ${offerAnalysis.job_salary.min?.toLocaleString() || 'N/A'}
                      </div>
                      <div className="text-gray-700">
                        Max: ${offerAnalysis.job_salary.max?.toLocaleString() || 'N/A'}
                      </div>
                    </div>
                    <div>
                      <h3 className="font-semibold mb-2">Market Salary</h3>
                      <div className="text-gray-700">
                        Min: ${offerAnalysis.market_salary.min?.toLocaleString() || 'N/A'}
                      </div>
                      <div className="text-gray-700">
                        Max: ${offerAnalysis.market_salary.max?.toLocaleString() || 'N/A'}
                      </div>
                    </div>
                  </div>
                  
                  <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                    <h3 className="font-semibold mb-2">Recommendation</h3>
                    <p className="text-gray-700">{offerAnalysis.recommendation}</p>
                  </div>
                  
                  <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                    <h3 className="font-semibold mb-2">Negotiation Potential</h3>
                    <p className="text-gray-700 capitalize">{offerAnalysis.negotiation_potential}</p>
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
