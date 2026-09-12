'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [stats, setStats] = useState({
    totalMatches: 0,
    pendingApplications: 0,
    viewedJobs: 0,
    unreadNotifications: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    fetchUserData();
    fetchStats();
  }, [router]);

  const fetchUserData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      }
    } catch (error) {
      console.error('Error fetching user data:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('token');
      // Mock stats for now - replace with actual API calls
      setStats({
        totalMatches: 12,
        pendingApplications: 5,
        viewedJobs: 8,
        unreadNotifications: 3,
      });
    } catch (error) {
      console.error('Error fetching stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    router.push('/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-indigo-600">AI Job Matching</h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-600">Welcome, {user?.full_name || user?.username}</span>
            <button
              onClick={handleLogout}
              className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Stats Cards */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-3xl font-bold text-indigo-600">{stats.totalMatches}</div>
            <div className="text-gray-600 mt-2">Total Matches</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-3xl font-bold text-green-600">{stats.pendingApplications}</div>
            <div className="text-gray-600 mt-2">Pending Applications</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-3xl font-bold text-blue-600">{stats.viewedJobs}</div>
            <div className="text-gray-600 mt-2">Viewed Jobs</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-3xl font-bold text-orange-600">{stats.unreadNotifications}</div>
            <div className="text-gray-600 mt-2">Unread Notifications</div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
          <div className="grid md:grid-cols-3 gap-4">
            <Link
              href="/upload-cv"
              className="bg-indigo-50 border-2 border-indigo-200 p-4 rounded-lg hover:bg-indigo-100 transition text-center"
            >
              <div className="text-2xl mb-2">📄</div>
              <div className="font-semibold">Upload CV</div>
              <div className="text-sm text-gray-600">Add or update your CV</div>
            </Link>
            <Link
              href="/recommendations"
              className="bg-green-50 border-2 border-green-200 p-4 rounded-lg hover:bg-green-100 transition text-center"
            >
              <div className="text-2xl mb-2">🎯</div>
              <div className="font-semibold">View Matches</div>
              <div className="text-sm text-gray-600">See your job matches</div>
            </Link>
            <Link
              href="/jobs"
              className="bg-blue-50 border-2 border-blue-200 p-4 rounded-lg hover:bg-blue-100 transition text-center"
            >
              <div className="text-2xl mb-2">🔍</div>
              <div className="font-semibold">Browse Jobs</div>
              <div className="text-sm text-gray-600">Search all available jobs</div>
            </Link>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
          <div className="space-y-4">
            <div className="flex items-center gap-4 p-3 bg-gray-50 rounded">
              <div className="text-green-500">✓</div>
              <div>
                <div className="font-medium">New job matches found</div>
                <div className="text-sm text-gray-600">2 hours ago</div>
              </div>
            </div>
            <div className="flex items-center gap-4 p-3 bg-gray-50 rounded">
              <div className="text-blue-500">👁</div>
              <div>
                <div className="font-medium">Your CV was viewed by Tech Corp</div>
                <div className="text-sm text-gray-600">1 day ago</div>
              </div>
            </div>
            <div className="flex items-center gap-4 p-3 bg-gray-50 rounded">
              <div className="text-orange-500">📝</div>
              <div>
                <div className="font-medium">Application submitted for Senior Developer</div>
                <div className="text-sm text-gray-600">3 days ago</div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
