'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function NetworkAnalysisPage() {
  const router = useRouter();
  const [networkAnalysis, setNetworkAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    fetchNetworkAnalysis();
  }, [router]);

  const fetchNetworkAnalysis = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/matching/network/analysis', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const analysisData = await response.json();
        setNetworkAnalysis(analysisData);
      }
    } catch (error) {
      console.error('Error fetching network analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading network analysis...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-indigo-600">Network Analysis</h1>
          <button
            onClick={() => router.push('/dashboard')}
            className="text-gray-600 hover:text-gray-900"
          >
            ← Back to Dashboard
          </button>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Professional Network Analysis</h2>
          
          {networkAnalysis ? (
            <div>
              <div className="mb-6">
                <div className="text-sm text-gray-600 mb-1">Networking Strength</div>
                <div className="text-3xl font-bold text-indigo-600">{networkAnalysis.networking_strength}%</div>
                <div className="text-lg font-semibold capitalize">{networkAnalysis.networking_rating}</div>
              </div>
              
              <div className="mb-6">
                <h3 className="font-semibold mb-2">Recommended Events</h3>
                <div className="space-y-2">
                  {networkAnalysis.recommended_events.slice(0, 3).map((event: any, index: number) => (
                    <div key={index} className="p-3 border border-gray-200 rounded-lg">
                      <div className="font-semibold">{event.name}</div>
                      <div className="text-sm text-gray-600">{event.type} - {event.frequency}</div>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="mb-6">
                <h3 className="font-semibold mb-2">Recommended Communities</h3>
                <div className="space-y-2">
                  {networkAnalysis.recommended_communities.slice(0, 3).map((community: any, index: number) => (
                    <div key={index} className="p-3 border border-gray-200 rounded-lg">
                      <div className="font-semibold">{community.name}</div>
                      <div className="text-sm text-gray-600">{community.type}</div>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="mb-6">
                <h3 className="font-semibold mb-2">Networking Tips</h3>
                <ul className="list-disc list-inside space-y-1">
                  {networkAnalysis.networking_tips.map((tip: string, index: number) => (
                    <li key={index} className="text-gray-700">{tip}</li>
                  ))}
                </ul>
              </div>
              
              <div>
                <h3 className="font-semibold mb-2">Networking Goals</h3>
                <ul className="list-disc list-inside space-y-1">
                  {networkAnalysis.networking_goals.map((goal: string, index: number) => (
                    <li key={index} className="text-gray-700">{goal}</li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            <div className="text-gray-500">Upload your CV to get personalized network analysis</div>
          )}
        </div>
      </main>
    </div>
  );
}
