'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function RecommendationsPage() {
  const router = useRouter();
  const [matches, setMatches] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCV, setSelectedCV] = useState<number | null>(null);
  const [cvs, setCvs] = useState<any[]>([]);

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
      const response = await fetch('http://localhost:8000/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const userData = await response.json();
        const cvsResponse = await fetch(`http://localhost:8000/api/cv/user/${userData.id}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (cvsResponse.ok) {
          const cvsData = await cvsResponse.json();
          setCvs(cvsData);
          if (cvsData.length > 0) {
            setSelectedCV(cvsData[0].id);
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
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/matching/cv/${cvId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const matchesData = await response.json();
        setMatches(matchesData);
      }
    } catch (error) {
      console.error('Error fetching matches:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFindMatches = () => {
    if (selectedCV) {
      setLoading(true);
      fetchMatches(selectedCV);
    }
  };

  const getMatchScoreColor = (score: number) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
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
        {/* CV Selection */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-bold mb-4">Select CV for Matching</h2>
          {cvs.length === 0 ? (
            <div className="text-gray-600">
              No CVs uploaded. <button onClick={() => router.push('/upload-cv')} className="text-indigo-600 hover:underline">Upload a CV</button>
            </div>
          ) : (
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
          )}
        </div>

        {/* Matches */}
        {loading ? (
          <div className="text-center py-8">
            <div className="text-xl">Finding matches...</div>
          </div>
        ) : matches.length === 0 ? (
          <div className="bg-white rounded-lg shadow-md p-8 text-center">
            <div className="text-gray-600">
              {selectedCV ? 'No matches found. Try selecting a different CV or upload a new one.' : 'Select a CV to find matches'}
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <h2 className="text-xl font-bold mb-4">Your Job Matches</h2>
            {matches.map((match) => (
              <div key={match.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-xl font-bold text-gray-900">Job #{match.job_id}</h3>
                      <div className={`text-white px-3 py-1 rounded-full text-sm font-bold ${getMatchScoreColor(match.match_score)}`}>
                        {match.match_score}% Match
                      </div>
                    </div>
                    <div className="flex gap-4 text-sm text-gray-600 mb-3">
                      <span className="flex items-center gap-1">
                        Status: {match.status}
                      </span>
                    </div>
                  </div>
                  <div className="flex flex-col gap-2 ml-4">
                    <button className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition">
                      Apply
                    </button>
                    <button className="bg-gray-200 text-gray-800 px-4 py-2 rounded-lg hover:bg-gray-300 transition">
                      View Details
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
