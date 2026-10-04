'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function LearningHubPage() {
  const router = useRouter();
  const [learningPlan, setLearningPlan] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    fetchLearningPlan();
  }, [router]);

  const fetchLearningPlan = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/matching/learning/plan', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const planData = await response.json();
        setLearningPlan(planData);
      }
    } catch (error) {
      console.error('Error fetching learning plan:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading personalized learning plan...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-indigo-600">Learning Hub</h1>
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
          <h2 className="text-xl font-semibold mb-4">Personalized Learning Plan</h2>
          
          {learningPlan ? (
            <div>
              <div className="mb-4">
                <div className="text-sm text-gray-600">Field</div>
                <div className="text-lg font-semibold capitalize">{learningPlan.field.replace('_', ' ')}</div>
              </div>
              
              <div className="mb-4">
                <div className="text-sm text-gray-600">Total Estimated Duration</div>
                <div className="text-lg font-semibold">{learningPlan.total_estimated_duration}</div>
              </div>
              
              <div className="mb-4">
                <h3 className="font-semibold mb-2">Recommended Start</h3>
                <p className="text-gray-700">{learningPlan.recommended_start?.skill}</p>
                <p className="text-sm text-gray-600">{learningPlan.recommended_start?.reason}</p>
              </div>
              
              <div>
                <h3 className="font-semibold mb-2">Skills to Learn</h3>
                <div className="space-y-4">
                  {learningPlan.skills_to_learn.slice(0, 5).map((skill: any, index: number) => (
                    <div key={index} className="p-4 border border-gray-200 rounded-lg">
                      <h4 className="font-semibold capitalize">{skill.skill}</h4>
                      <div className="text-sm text-gray-600">Priority: {skill.priority}%</div>
                      <div className="text-sm text-gray-600">Duration: {skill.estimated_duration}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="text-gray-500">Upload your CV to get a personalized learning plan</div>
          )}
        </div>
      </main>
    </div>
  );
}
