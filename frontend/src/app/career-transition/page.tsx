'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function CareerTransitionPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [transitionPaths, setTransitionPaths] = useState<any[]>([]);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    fetchTransitionPaths();
  }, [router]);

  const fetchTransitionPaths = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/matching/career-transition/paths', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const pathsData = await response.json();
        setTransitionPaths(pathsData);
      }
    } catch (error) {
      console.error('Error fetching transition paths:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading career transition options...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-indigo-600">Career Transition</h1>
          <button
            onClick={() => router.push('/dashboard')}
            className="text-gray-600 hover:text-gray-900"
          >
            ← Back to Dashboard
          </button>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">Career Transition Paths</h2>
          <p className="text-gray-600 mb-4">Explore different career paths based on your transferable skills</p>
          
          {transitionPaths.length > 0 ? (
            <div className="space-y-4">
              {transitionPaths.map((path, index) => (
                <div key={index} className="p-4 border border-gray-200 rounded-lg">
                  <h3 className="font-semibold capitalize">{path.target_field.replace('_', ' ')}</h3>
                  <div className="grid md:grid-cols-3 gap-4 mt-2">
                    <div>
                      <div className="text-sm text-gray-600">Transferability Score</div>
                      <div className="text-lg font-bold text-blue-600">{path.transferability_score}%</div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600">Success Probability</div>
                      <div className="text-lg font-bold text-green-600">{path.success_probability}%</div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-600">Difficulty</div>
                      <div className="text-lg font-bold capitalize">{path.transition_difficulty}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-gray-500">Upload your CV to see personalized career transition options</div>
          )}
        </div>
      </main>
    </div>
  );
}
