'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function InterviewPrepPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<any[]>([]);
  const [selectedJob, setSelectedJob] = useState<any>(null);
  const [interviewQuestions, setInterviewQuestions] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [userAnswer, setUserAnswer] = useState('');
  const [answerAnalysis, setAnswerAnalysis] = useState<any>(null);

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
        setJobs(jobsData.slice(0, 10)); // Show first 10 jobs
      }
    } catch (error) {
      console.error('Error fetching jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  const selectJob = async (job: any) => {
    setSelectedJob(job);
    setLoading(true);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`/api/matching/interview-preparation/${job.external_id}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const questionsData = await response.json();
        setInterviewQuestions(questionsData);
        setCurrentQuestion(0);
      }
    } catch (error) {
      console.error('Error fetching interview questions:', error);
    } finally {
      setLoading(false);
    }
  };

  const analyzeAnswer = async () => {
    if (!userAnswer || !interviewQuestions) return;

    try {
      const allQuestions = [
        ...interviewQuestions.technical_questions,
        ...interviewQuestions.behavioral_questions,
        ...interviewQuestions.job_specific_questions
      ];
      
      const currentQ = allQuestions[currentQuestion];
      
      const response = await fetch('/api/matching/interview-preparation/analyze-answer', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: currentQ,
          answer: userAnswer
        })
      });

      if (response.ok) {
        const analysisData = await response.json();
        setAnswerAnalysis(analysisData);
      }
    } catch (error) {
      console.error('Error analyzing answer:', error);
    }
  };

  const nextQuestion = () => {
    if (interviewQuestions) {
      const totalQuestions = 
        interviewQuestions.technical_questions.length +
        interviewQuestions.behavioral_questions.length +
        interviewQuestions.job_specific_questions.length;
      
      if (currentQuestion < totalQuestions - 1) {
        setCurrentQuestion(currentQuestion + 1);
        setUserAnswer('');
        setAnswerAnalysis(null);
      }
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading interview preparation...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-indigo-600">Interview Preparation</h1>
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
            <h2 className="text-xl font-semibold mb-4">Select a Job to Practice Interviews</h2>
            <div className="grid md:grid-cols-2 gap-4">
              {jobs.map((job) => (
                <div
                  key={job.external_id}
                  onClick={() => selectJob(job)}
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
              <p className="text-gray-600 mb-4">Interview Practice Session</p>
              
              {interviewQuestions && (
                <div className="border-t pt-4">
                  <div className="mb-4">
                    <span className="text-sm text-gray-600">Question {currentQuestion + 1} of {
                      interviewQuestions.technical_questions.length +
                      interviewQuestions.behavioral_questions.length +
                      interviewQuestions.job_specific_questions.length
                    }</span>
                  </div>
                  
                  <div className="mb-4">
                    <h3 className="font-semibold mb-2">Question:</h3>
                    <p className="text-gray-700">
                      {[
                        ...interviewQuestions.technical_questions,
                        ...interviewQuestions.behavioral_questions,
                        ...interviewQuestions.job_specific_questions
                      ][currentQuestion]}
                    </p>
                  </div>
                  
                  <div className="mb-4">
                    <h3 className="font-semibold mb-2">Your Answer:</h3>
                    <textarea
                      value={userAnswer}
                      onChange={(e) => setUserAnswer(e.target.value)}
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                      rows={4}
                      placeholder="Type your answer here..."
                    />
                  </div>
                  
                  <div className="flex gap-2">
                    <button
                      onClick={analyzeAnswer}
                      className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700"
                    >
                      Analyze Answer
                    </button>
                    <button
                      onClick={nextQuestion}
                      className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300"
                    >
                      Next Question
                    </button>
                  </div>
                  
                  {answerAnalysis && (
                    <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                      <h4 className="font-semibold mb-2">Answer Analysis</h4>
                      <p className="text-sm text-gray-700 mb-2">Score: {answerAnalysis.score}/100</p>
                      <p className="text-sm text-gray-700 mb-2">{answerAnalysis.feedback}</p>
                      {answerAnalysis.strengths.length > 0 && (
                        <div className="mb-2">
                          <p className="text-sm font-semibold text-green-700">Strengths:</p>
                          <ul className="list-disc list-inside text-sm text-gray-700">
                            {answerAnalysis.strengths.map((strength: string, index: number) => (
                              <li key={index}>{strength}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {answerAnalysis.improvements.length > 0 && (
                        <div>
                          <p className="text-sm font-semibold text-orange-700">Improvements:</p>
                          <ul className="list-disc list-inside text-sm text-gray-700">
                            {answerAnalysis.improvements.map((improvement: string, index: number) => (
                              <li key={index}>{improvement}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
            
            {interviewQuestions && (
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="font-semibold mb-4">Preparation Tips</h3>
                <ul className="list-disc list-inside space-y-2">
                  {interviewQuestions.preparation_tips.map((tip: string, index: number) => (
                    <li key={index} className="text-gray-700">{tip}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
